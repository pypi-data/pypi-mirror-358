import json
import os

from synapse_sdk.utils.converters import ToDMConverter


class COCOToDMConverter(ToDMConverter):
    """Convert COCO format annotations to DM (Data Manager) format."""

    def convert(self):
        if self.is_categorized_dataset:
            splits = self._validate_splits(['train', 'valid'], ['test'])
            all_split_data = {}
            for split, split_dir in splits.items():
                annotation_path = os.path.join(split_dir, 'annotations.json')
                if not os.path.exists(annotation_path):
                    raise FileNotFoundError(f'annotations.json not found in {split_dir}')
                with open(annotation_path, 'r', encoding='utf-8') as f:
                    coco_data = json.load(f)
                split_data = self._convert_coco_ann_to_dm(coco_data, split_dir)
                all_split_data[split] = split_data
            self.converted_data = all_split_data
            return all_split_data
        else:
            annotation_path = os.path.join(self.root_dir, 'annotations.json')
            if not os.path.exists(annotation_path):
                raise FileNotFoundError(f'annotations.json not found in {self.root_dir}')
            with open(annotation_path, 'r', encoding='utf-8') as f:
                coco_data = json.load(f)
            converted_data = self._convert_coco_ann_to_dm(coco_data, self.root_dir)
            self.converted_data = converted_data
            return converted_data

    def _convert_coco_ann_to_dm(self, coco_data, base_dir):
        """Convert COCO annotations to DM format."""
        dataset_type = coco_data.get('type', 'image')  # Default to 'image' if type is not specified
        if dataset_type == 'image':
            return self._process_image_data(coco_data, base_dir)
        else:
            raise ValueError(f'Unsupported dataset type: {dataset_type}')

    def _process_image_data(self, coco_data, img_base_dir):
        """Process COCO image data and convert to DM format."""
        images = coco_data.get('images', [])
        annotations = coco_data.get('annotations', [])
        categories = coco_data.get('categories', [])
        cat_map = {cat['id']: cat for cat in categories}

        # Build image_id -> annotation list
        ann_by_img_id = {}
        for ann in annotations:
            img_id = ann['image_id']
            ann_by_img_id.setdefault(img_id, []).append(ann)

        result = {}
        for img in images:
            img_id = img['id']
            img_filename = img['file_name']
            img_path = os.path.join(img_base_dir, img_filename)
            anns = ann_by_img_id.get(img_id, [])

            # DM image structure
            dm_img = {
                'bounding_box': [],
                'keypoint': [],
                'relation': [],
                'group': [],
            }

            # Handle bounding_box
            bbox_ids = []
            for ann in anns:
                cat = cat_map.get(ann['category_id'], {})
                if 'bbox' in ann and ann['bbox']:
                    bbox_id = self._generate_unique_id()
                    bbox_ids.append(bbox_id)
                    dm_img['bounding_box'].append({
                        'id': bbox_id,
                        'classification': cat.get('name', str(ann['category_id'])),
                        'attrs': ann.get('attrs', []),
                        'data': list(ann['bbox']),
                    })

            # Handle keypoints
            for ann in anns:
                cat = cat_map.get(ann['category_id'], {})
                attrs = ann.get('attrs', [])
                if 'keypoints' in ann and ann['keypoints']:
                    kp_names = cat.get('keypoints', [])
                    kps = ann['keypoints']
                    keypoint_ids = []
                    for idx in range(min(len(kps) // 3, len(kp_names))):
                        x, y, v = kps[idx * 3 : idx * 3 + 3]
                        kp_id = self._generate_unique_id()
                        keypoint_ids.append(kp_id)
                        dm_img['keypoint'].append({
                            'id': kp_id,
                            'classification': kp_names[idx] if idx < len(kp_names) else f'keypoint_{idx}',
                            'attrs': attrs,
                            'data': [x, y],
                        })
                    group_ids = bbox_ids + keypoint_ids
                    if group_ids:
                        dm_img['group'].append({
                            'id': self._generate_unique_id(),
                            'classification': cat.get('name', str(ann['category_id'])),
                            'attrs': attrs,
                            'data': group_ids,
                        })

            dm_json = {'images': [dm_img]}
            result[img_filename] = (dm_json, img_path)
        return result
