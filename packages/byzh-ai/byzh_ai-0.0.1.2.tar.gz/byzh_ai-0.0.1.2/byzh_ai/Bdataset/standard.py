import numpy as np
import torch


def b_data_standard1d(template_data, datas: list, dim=(0, 2)):
    '''
    对数据进行标准化
    :param template_data: 用于计算mean和std的模板数据
    :param datas: 待标准化的数据
    :param dim: dim=(0, 2)代表 每个通道(dim=1)单独标准化
    :return:
    '''
    if type(template_data) == torch.Tensor:
        mean = torch.mean(template_data, dim=dim, keepdim=True)
        std = torch.std(template_data, dim=dim, keepdim=True) + 1e-8
    else:
        mean = np.mean(template_data, axis=dim, keepdims=True)
        std = np.std(template_data, axis=dim, keepdims=True) + 1e-8

    results = []
    for target_data in datas:
        target_data = (target_data - mean) / std
        results.append(target_data)

    return results

def b_data_standard2d(template_data, datas: list, dim=(0, 2, 3)):
    '''
    对数据进行标准化
    :param template_data: 用于计算mean和std的模板数据
    :param datas: 待标准化的数据
    :param dim: dim=(0, 2, 3)代表 每个通道(dim=1)单独标准化
    :return:
    '''
    if type(template_data) == torch.Tensor:
        mean = torch.mean(template_data, dim=dim, keepdim=True)
        std = torch.std(template_data, dim=dim, keepdim=True) + 1e-8
    else:
        mean = np.mean(template_data, axis=dim, keepdims=True)
        std = np.std(template_data, axis=dim, keepdims=True) + 1e-8

    results = []
    for target_data in datas:
        target_data = (target_data - mean) / std
        results.append(target_data)
    return results
