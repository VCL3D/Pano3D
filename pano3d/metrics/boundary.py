import torch
from scipy import ndimage


class DbeCom(torch.nn.Module):
    def __init__(self,
        max_dist_thr: float=10.0, # Threshold for local neighborhood
    ):
        """
        Completeness: sum of undirected chamfer distances of predicted and gt edges
        This measure takes into account missing edges in the predicted depth image.
        reference: https://openaccess.thecvf.com/content_ECCVW_2018/papers/11131/Koch_Evaluation_of_CNN-based_Single-Image_Depth_Estimation_Methods_ECCVW_2018_paper.pdf

        """
        super(DbeCom, self).__init__()
        self.max_dist_thr = max_dist_thr

    def forward(self, 
        gt:          torch.Tensor, #gt edges
        pred:       torch.Tensor, #pred edges
    ):        
        # compute distance transform for chamfer metric
        D_gt  = ndimage.distance_transform_edt(1-gt.cpu())
        D_est = ndimage.distance_transform_edt(1-pred.cpu())

        mask_D_gt = D_gt<self.max_dist_thr # truncate distance transform map

        E_fin_est_filt = pred.cpu()*mask_D_gt # compute shortest distance for all predicted edges

        if E_fin_est_filt.sum() == 0: # assign MAX value if no edges could be detected in prediction
            dbe_com =  torch.tensor(self.max_dist_thr)
        else:
            # completeness: sum of undirected chamfer distances of predicted and gt edges
            ch1 = torch.from_numpy(D_gt)*pred.cpu() 
            ch1[ch1>self.max_dist_thr] = self.max_dist_thr #truncate distances
            ch2 = torch.from_numpy(D_est)*gt.cpu()
            ch2[ch2>self.max_dist_thr] = self.max_dist_thr # truncate distances
            res = ch1+ch2 # summed distances
            dbe_com = torch.sum(res, dim = (1,2,3)) / (torch.sum(pred.cpu(),dim = (1,2,3)) + torch.sum(gt.cpu(),dim = (1,2,3))).mean()

        return dbe_com

class DbeAcc(torch.nn.Module):
    def __init__(self,
        max_dist_thr: float=10.0, # Threshold for local neighborhood
    ):
        """
        Accuracy metric: directed chamfer distance of predicted edges towards gt edges
        
        reference: https://openaccess.thecvf.com/content_ECCVW_2018/papers/11131/Koch_Evaluation_of_CNN-based_Single-Image_Depth_Estimation_Methods_ECCVW_2018_paper.pdf

        """
        super(DbeAcc, self).__init__()
        self.max_dist_thr = max_dist_thr

    def forward(self, 
        gt:         torch.Tensor,
        pred:       torch.Tensor,
    ):        
        # compute distance transform for chamfer metric
        D_gt  = ndimage.distance_transform_edt(1-gt.cpu())
        #D_est = ndimage.distance_transform_edt(1-pred.cpu())

        mask_D_gt = D_gt<self.max_dist_thr # truncate distance transform map

        E_fin_est_filt = pred.cpu()*mask_D_gt # compute shortest distance for all predicted edges

        if E_fin_est_filt.sum() == 0: # assign MAX value if no edges could be detected in prediction
            dbe_acc = torch.tensor(self.max_dist_thr)
        else:
            #accuracy: directed chamfer distance of predicted edges towards gt edges per batch
            dbe_acc = torch.sum(torch.from_numpy(D_gt)*E_fin_est_filt, dim = (1,2,3)) / torch.sum(E_fin_est_filt,dim = (1,2,3)).mean()

        return dbe_acc

class EdgePre(torch.nn.Module):
    def __init__(self,

    ):
        """
        Edge precision metric.
        reference: https://arxiv.org/pdf/1803.08673.pdf
        """
        super(EdgePre, self).__init__()

    def forward(self, 
        gt:          torch.Tensor,
        pred:       torch.Tensor,
    ):        
        
        b , _ , __ , ___ = gt.shape
        prec_  = torch.zeros(b)
        for i in range(b):
            if (torch.where(gt[i]==1,1,0).sum() == 0):
                #no gt edges
                prec_[i] = 1
            else:
                false_positives = torch.where((gt[i]!=1) & (pred[i] == 1),1,0).sum()
                true_positives = torch.where((gt[i]==1) & (pred[i] == 1),1,0).sum()
                if torch.where(pred[i] == 1,1,0).sum() == 0:
                    prec_[i] = 0
                else:
                    prec_[i] = true_positives/(true_positives + false_positives) # , or the accuracy of minority class predictions
        
        return prec_.mean()

class EdgeRec(torch.nn.Module):
    def __init__(self,

    ):
        """
        Edge recall metric.
        reference: https://arxiv.org/pdf/1803.08673.pdf
        """
        super(EdgeRec, self).__init__()

    def forward(self, 
        gt:          torch.Tensor,
        pred:       torch.Tensor,
    ):        
        
        #if image has no edges
        b , _ , __ , ___ = gt.shape
        recall_  = torch.zeros(b)
        for i in range(b):
            if torch.where(gt[i]==1,1,0).sum() == 0:
                #no gt edges
                recall_[i] = 1
            else:
                false_positives = torch.where((gt[i]!=1) & (pred[i] == 1),1,0).sum()
                true_positives = torch.where((gt[i]==1) & (pred[i] == 1),1,0).sum()
                false_negatives = torch.where((gt[i]!=0) & (pred[i] == 0),1,0).sum()
                recall_[i] = true_positives / (true_positives + false_negatives) #low recall a lot of missed edges -- our model needs to catch this better;
                
        return recall_.mean()