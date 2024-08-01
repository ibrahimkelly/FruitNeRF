"""
Copyright (c) 2023 Lukas Meyer
Licensed under the MIT License.
See LICENSE file for more information.
"""
import copy
# Built-in/Generic Imports
from typing import Union, Literal

# Libs
import open3d as o3d
import numpy as np
from pathlib import Path
import alphashape

# Own modules
from clustering_base import (load_obj_file,
                             FruitClustering)


class Clustering(FruitClustering):
    def __init__(self,
                 shape_method: Literal['distance', 'ransac', 'svd'] = 'distance',
                 template_path: Union[str, Path] = './clustering/apple_template.ply',
                 voxel_size_down_sample: float = 0.00005,
                 remove_outliers_nb_points: int = 800,
                 remove_outliers_radius: float = 0.02,
                 min_samples: int = 60,
                 apple_template_size: float = 0.8,
                 cluster_merge_distance: float = 0.04,
                 gt_cluster=None,
                 gt_count: int = None):
        super().__init__(voxel_size_down_sample=voxel_size_down_sample,
                         remove_outliers_nb_points=remove_outliers_nb_points,
                         remove_outliers_radius=remove_outliers_radius,
                         cluster_merge_distance=cluster_merge_distance)
        self.shape_method: Literal['distance', 'ransac'] = shape_method
        self.template_path = template_path

        self.min_samples = min_samples

        self.fruit_template = o3d.io.read_point_cloud(self.template_path)
        self.fruit_template = self.fruit_template.scale(apple_template_size, center=(0, 0, 0))
        self.fruit_template = self.fruit_template.translate(-self.fruit_template.get_center())
        self.fruit_alpha_shape_ = alphashape.alphashape(np.asarray(self.fruit_template.points), 10)
        self.fruit_alpha_shape = self.fruit_alpha_shape_.as_open3d.sample_points_uniformly(1000)
        # o3d.visualization.draw_geometries([self.fruit_template])

        self.gt_cluster = gt_cluster
        if self.gt_cluster:
            if "obj" in self.gt_cluster:
                self.gt_mesh, self.gt_cluster_center, self.gt_cluster_pcd = load_obj_file(gt_cluster)
                # self.gt_position = o3d.io.read_point_cloud(self.gt_cluster)
                # self.gt_position.paint_uniform_color([1,0,1])
                self.gt_position = o3d.geometry.PointCloud()
                self.gt_position.points = o3d.utility.Vector3dVector(np.vstack(self.gt_cluster_center))
                # self.gt_position = self.gt_cluster_center

            else:
                self.gt_position = o3d.io.read_line_set(self.gt_cluster)

        self.gt_count = gt_count


if __name__ == '__main__':

    from clustering.config_synthetic import (Apple_GT_1024x1024_300, Apple_SAM_1024x1024_300,
                                             Pear_GT_1024x1024_300, Pear_SAM_1024x1024_300,
                                             Plum_GT_1024x1024_300, Plum_SAM_1024x1024_300,
                                             Lemon_GT_1024x1024_300, Lemon_SAM_1024x1024_300,
                                             Peach_GT_1024x1024_300, Peach_SAM_1024x1024_300,
                                             Mango_GT_1024x1024_300, Mango_SAM_1024x1024_300)

    from clustering.config_real import (Baum_01_unet, Baum_01_unet_Big, Baum_01_SAM, Baum_01_SAM_Big,
                                        Baum_02_unet, Baum_02_unet_Big, Baum_02_SAM, Baum_02_SAM_Big,
                                        Baum_03_unet, Baum_03_unet_Big, Baum_03_SAM, Baum_03_SAM_Big)

    from clustering.config_real import Fuji_unet, Fuji_unet_big, Fuji_sam, Fuji_sam_big

    Fuji_sam_sweep = {
        "path": "/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply",
        "remove_outliers_nb_points": [50, 60, 75],
        "remove_outliers_radius": 0.025,
        "down_sample": 0.001,
        "eps": [0.015, 0.02],
        "cluster_merge_distance": 0.04,
        "minimum_size_factor": 0.2,
        "min_samples": 100,
        'template_path': './clustering/apple_template.ply',
        'apple_template_size': [0.9, 1, 1.1],
        "gt_cluster": "/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/data/lineset_aligned.ply",
        "gt_count": 1455
    }

    Fuji_sam_big_sweep = {
        "path": "/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam_big/semantic_colormap_cropped.ply",
        "remove_outliers_nb_points": [50, 60, 75],
        "remove_outliers_radius": 0.025,
        "down_sample": 0.001,
        "eps": [0.015, 0.02],
        "cluster_merge_distance": 0.04,
        "minimum_size_factor": 0.2,
        "min_samples": 100,
        'template_path': './clustering/apple_template.ply',
        'apple_template_size': [0.9, 1, 1.1],
        "gt_cluster": "/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/data/lineset_aligned.ply",
        "gt_count": 1455
    }

    Baum = Fuji_sam_big_sweep

    results = {}

    cc = 0

    for remove_outliers_nb_points in Baum["remove_outliers_nb_points"]:
        for eps in Baum["eps"]:
            for apple_template_size in Baum["apple_template_size"]:

                clustering = Clustering(remove_outliers_nb_points=remove_outliers_nb_points,
                                        remove_outliers_radius=Baum['remove_outliers_radius'],
                                        voxel_size_down_sample=Baum['down_sample'],
                                        template_path=Baum['template_path'],
                                        min_samples=Baum['min_samples'],
                                        apple_template_size=apple_template_size,
                                        gt_cluster=Baum['gt_cluster'],
                                        cluster_merge_distance=Baum['cluster_merge_distance'],
                                        gt_count=Baum['gt_count']
                                        )
                count = clustering.count(pcd=Baum["path"], eps=eps, )

                if Baum['gt_cluster']:
                    results.update({cc: {
                        "path": Baum['path'],
                        'count': count,
                        'TP': clustering.true_positive,
                        'gt': clustering.gt_count,
                        'precision': clustering.precision,
                        'recall': clustering.recall,
                        'F1': clustering.F1,
                        'params': {
                            'remove_outliers_nb_points': remove_outliers_nb_points,
                            'eps': eps,
                            'apple_template_size': apple_template_size,
                        }
                    }})
                else:
                    results.update({cc: {
                        "path": Baum['path'],
                        'count': count,
                        'gt': clustering.gt_count,
                    }})
                cc += 1

                print(results)
        print("\n --------------------------------- \n")
    print(results)

    import json

    with open('./clustering/results_synthetic.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


#         "path": "/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply",
{0: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 1059, 'TP': 959, 'gt': 1455, 'precision': 0.9055712936732767, 'recall': 0.659106529209622,
     'F1': 0.7629276054097055, 'params': {'remove_outliers_nb_points': 50, 'eps': 0.015, 'apple_template_size': 0.9}},
 1: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 858, 'TP': 814, 'gt': 1455, 'precision': 0.9487179487179487, 'recall': 0.5594501718213059,
     'F1': 0.7038478166882837, 'params': {'remove_outliers_nb_points': 50, 'eps': 0.015, 'apple_template_size': 1}},
 2: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 654, 'TP': 645, 'gt': 1455, 'precision': 0.9862385321100917, 'recall': 0.44329896907216493,
     'F1': 0.6116642958748222, 'params': {'remove_outliers_nb_points': 50, 'eps': 0.015, 'apple_template_size': 1.1}},
 3: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 1175, 'TP': 1037, 'gt': 1455, 'precision': 0.8825531914893617, 'recall': 0.7127147766323024,
     'F1': 0.7885931558935361, 'params': {'remove_outliers_nb_points': 50, 'eps': 0.02, 'apple_template_size': 0.9}},
 4: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 970, 'TP': 906, 'gt': 1455, 'precision': 0.934020618556701, 'recall': 0.622680412371134,
     'F1': 0.7472164948453609, 'params': {'remove_outliers_nb_points': 50, 'eps': 0.02, 'apple_template_size': 1}},
 5: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 776, 'TP': 755, 'gt': 1455, 'precision': 0.9729381443298969, 'recall': 0.5189003436426117,
     'F1': 0.6768265351860152, 'params': {'remove_outliers_nb_points': 50, 'eps': 0.02, 'apple_template_size': 1.1}},
 6: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 1077, 'TP': 958, 'gt': 1455, 'precision': 0.8895078922934077, 'recall': 0.6584192439862543,
     'F1': 0.7567140600315956, 'params': {'remove_outliers_nb_points': 60, 'eps': 0.015, 'apple_template_size': 0.9}},
 7: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 857, 'TP': 809, 'gt': 1455, 'precision': 0.9439906651108518, 'recall': 0.5560137457044674,
     'F1': 0.6998269896193773, 'params': {'remove_outliers_nb_points': 60, 'eps': 0.015, 'apple_template_size': 1}},
 8: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 664, 'TP': 651, 'gt': 1455, 'precision': 0.9804216867469879, 'recall': 0.44742268041237115,
     'F1': 0.6144407739499764, 'params': {'remove_outliers_nb_points': 60, 'eps': 0.015, 'apple_template_size': 1.1}},
 9: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
     'count': 1178, 'TP': 1039, 'gt': 1455, 'precision': 0.8820033955857386, 'recall': 0.7140893470790378,
     'F1': 0.7892138245347512, 'params': {'remove_outliers_nb_points': 60, 'eps': 0.02, 'apple_template_size': 0.9}},
 10: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
      'count': 968, 'TP': 909, 'gt': 1455, 'precision': 0.9390495867768595, 'recall': 0.6247422680412371,
      'F1': 0.7503095336359884, 'params': {'remove_outliers_nb_points': 60, 'eps': 0.02, 'apple_template_size': 1}},
 11: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
      'count': 771, 'TP': 750, 'gt': 1455, 'precision': 0.9727626459143969, 'recall': 0.5154639175257731,
      'F1': 0.673854447439353, 'params': {'remove_outliers_nb_points': 60, 'eps': 0.02, 'apple_template_size': 1.1}},
 12: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
      'count': 1076, 'TP': 951, 'gt': 1455, 'precision': 0.8838289962825279, 'recall': 0.6536082474226804,
      'F1': 0.751481627815093, 'params': {'remove_outliers_nb_points': 75, 'eps': 0.015, 'apple_template_size': 0.9}},
 13: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
      'count': 842, 'TP': 805, 'gt': 1455, 'precision': 0.9560570071258907, 'recall': 0.5532646048109966,
      'F1': 0.7009142359599477, 'params': {'remove_outliers_nb_points': 75, 'eps': 0.015, 'apple_template_size': 1}},
 14: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
      'count': 662, 'TP': 650, 'gt': 1455, 'precision': 0.9818731117824774, 'recall': 0.44673539518900346,
      'F1': 0.6140765233821446, 'params': {'remove_outliers_nb_points': 75, 'eps': 0.015, 'apple_template_size': 1.1}},
 15: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
      'count': 1157, 'TP': 1021, 'gt': 1455, 'precision': 0.8824546240276577, 'recall': 0.7017182130584192,
      'F1': 0.7817764165390505, 'params': {'remove_outliers_nb_points': 75, 'eps': 0.02, 'apple_template_size': 0.9}},
 16: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
      'count': 964, 'TP': 897, 'gt': 1455, 'precision': 0.9304979253112033, 'recall': 0.6164948453608248,
      'F1': 0.7416287722199256, 'params': {'remove_outliers_nb_points': 75, 'eps': 0.02, 'apple_template_size': 1}},
 17: {'path': '/home/se86kimy/Dropbox/07_data/For5G/Apple_24_08_23/eval/fuji/sam/semantic_colormap_cropped.ply',
      'count': 757, 'TP': 738, 'gt': 1455, 'precision': 0.9749009247027741, 'recall': 0.5072164948453608,
      'F1': 0.6672694394213381, 'params': {'remove_outliers_nb_points': 75, 'eps': 0.02, 'apple_template_size': 1.1}}}
