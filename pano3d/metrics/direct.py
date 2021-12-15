
import torch
import functools
import typing

class Delta(torch.nn.Module):
    def __init__(self, 
        threshold: float=1.25
    ):
        super(Delta, self).__init__()
        self.threshold = threshold

    def forward(self,
        gt:             torch.Tensor,
        pred:           torch.Tensor,
        weights:        torch.Tensor=None,
    ) -> torch.Tensor: #NOTE: no mean
        errors =  (torch.max((gt / pred), (pred / gt)) < self.threshold).float()
        if weights is None:
            return torch.mean(errors)
        else:
            return torch.mean(
                torch.sum(errors * weights, dim=_dim_list(gt))
                / torch.sum(weights, dim=_dim_list(gt))
            )

Delta1 = functools.partial(Delta, threshold=1.25)
Delta2 = functools.partial(Delta, threshold=1.25 ** 2)
Delta3 = functools.partial(Delta, threshold=1.25 ** 3)

class AbsRel(torch.nn.Module):
    def __init__(self):
        super(AbsRel, self).__init__()

    def forward(self,
        gt:         torch.Tensor,
        pred:       torch.Tensor,
        weights:    torch.Tensor=None,
        mask:       torch.Tensor=None,
    ) -> torch.Tensor:
        absrel = torch.abs((gt - pred) / gt )
        if weights is not None:
            absrel = absrel * weights
        if mask is not None:
            absrel = absrel[mask]
        if weights is None:
            return torch.mean(torch.mean(absrel, dim=_dim_list(gt)))
        else:
            return torch.mean(
                torch.sum(absrel, dim=_dim_list(gt))
                / torch.sum(weights, dim=_dim_list(gt))
            )

class RMSE(torch.nn.Module):
    def __init__(self):
        super(RMSE, self).__init__()

    def forward(self,
        gt:         torch.Tensor,
        pred:       torch.Tensor,
        weights:    torch.Tensor=None,
        mask:       torch.Tensor=None,
    ) -> torch.Tensor:
        diff_sq = (gt - pred) ** 2
        if weights is not None:
            diff_sq = diff_sq * weights
        if mask is not None:
            diff_sq = diff_sq[mask]
        if weights is None:
            return torch.mean(torch.sqrt(torch.mean(diff_sq, dim=_dim_list(gt))))
        else:
            diff_sq_sum = torch.sum(diff_sq, dim=_dim_list(gt))
            diff_w_sum = torch.sum(weights, dim=_dim_list(gt)) # + 1e-18
            return torch.mean(torch.sqrt(diff_sq_sum / diff_w_sum))

class RMSLE(torch.nn.Module):
    def __init__(self,
        base: str='natural' # 'natural' or 'ten'
    ):
        super(RMSLE, self).__init__()
        self.log = torch.log if base == 'natural' else torch.log10

    def forward(self,
        gt:         torch.Tensor,
        pred:       torch.Tensor,
        weights:    torch.Tensor=None,
        mask:       torch.Tensor=None,
    ) -> torch.Tensor:
        pred_fix = torch.where(pred == 0.0,
            pred + 1e-24,
            pred
        )
        log_diff_sq = (self.log(gt) - self.log(pred_fix)) ** 2
        if weights is not None:
            log_diff_sq = log_diff_sq * weights
        if mask is not None:
            log_diff_sq = log_diff_sq[mask]
        if weights is None:
            return torch.mean(torch.sqrt(torch.mean(log_diff_sq, dim=_dim_list(gt))))
        else:
            log_diff_sq_sum = torch.sum(log_diff_sq, dim=_dim_list(gt))
            log_diff_w_sum = torch.sum(weights, dim=_dim_list(gt)) # + 1e-18
            return torch.mean(torch.sqrt(log_diff_sq_sum / log_diff_w_sum))


class SqRel(torch.nn.Module):
    def __init__(self):
        super(SqRel, self).__init__()

    def forward(self,
        gt:         torch.Tensor,
        pred:       torch.Tensor,
        weights:    torch.Tensor=None,
        mask:       torch.Tensor=None,
    ) -> torch.Tensor:
        sqrel = ((gt - pred) ** 2) / gt
        if weights is not None:
            sqrel = sqrel * weights
        if mask is not None:
            sqrel = sqrel[mask]
        if weights is None:
            return torch.mean(torch.mean(sqrel, dim=_dim_list(gt)))
        else:
            return torch.mean(
                torch.sum(sqrel, dim=_dim_list(gt))
                / torch.sum(weights, dim=_dim_list(gt))
            )


def _dim_list(
    tensor:         torch.Tensor,
    start_index:    int=1,
) -> typing.List[int]:
    return list(range(start_index, len(tensor.shape)))