from dataflow.mutations.formatters.dto import CompletedPipeline


class PipelineAnalyzer:
    @property
    def name(self) -> str:
        raise NotImplementedError()

    def show(self, pipeline: CompletedPipeline) -> None:
        raise NotImplementedError()
