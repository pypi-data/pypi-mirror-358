"""Recipe integrating Pointwise mesh generation jobs."""

from glacium.managers.RecipeManager import RecipeManager, BaseRecipe
from glacium.engines.PointwiseJobs import PointwiseGCIJob, PointwiseMesh2Job
from glacium.engines.fluent2fensap import Fluent2FensapJob

@RecipeManager.register
class PointwiseRecipe(BaseRecipe):
    """Run the Pointwise GCI and mesh generation scripts."""

    name = "pointwise"
    description = "Run Pointwise mesh scripts"

    def build(self, project):
        return [
            PointwiseGCIJob(project),
            PointwiseMesh2Job(project),
            Fluent2FensapJob(project),
        ]


