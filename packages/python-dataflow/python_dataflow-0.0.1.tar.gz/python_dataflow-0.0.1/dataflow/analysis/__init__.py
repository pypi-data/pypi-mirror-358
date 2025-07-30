from dataflow.analysis.base import PipelineAnalyzer
from dataflow.analysis.textual import TextualPipelineAnalyzer

ANALYZERS: dict[str, PipelineAnalyzer] = {
    analyzer.name: analyzer for analyzer in [
        TextualPipelineAnalyzer(),
    ]
}


def get_analyzer(analyzer: str) -> PipelineAnalyzer:
    return ANALYZERS[analyzer]
