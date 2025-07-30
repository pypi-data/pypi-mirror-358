from colorama import init, Fore

from dataflow.analysis.base import PipelineAnalyzer
from dataflow.mutations.formatters.dto import CompletedPipeline, CompletedMutationData


class TextualPipelineAnalyzer(PipelineAnalyzer):
    def __init__(self):
        super().__init__()
        init()

    @property
    def name(self) -> str:
        return "textual"

    def show_mutation(self, index: int, mutation_data: CompletedMutationData) -> None:
        print(f"{Fore.YELLOW}Mutation {index}: {Fore.GREEN}{mutation_data.name}")
        print(f"{Fore.WHITE}  ↳ Context: {Fore.LIGHTWHITE_EX}{mutation_data.context}")

        if mutation_data.validations:
            print(f"{Fore.WHITE}  ↳ Validations:")
            for validation_index, validation_data in enumerate(
                mutation_data.validations, start=1
            ):
                print(
                    f"    {Fore.BLUE}Validation {validation_index}: {Fore.GREEN}{validation_data.name}"
                )

                if validation_data.fails:
                    print(
                        f"      {Fore.RED}✗ {len(validation_data.fails)} "
                        f"Fail{'s' if len(validation_data.fails) > 1 else ''}:"
                    )

                    for fail in validation_data.fails:
                        print(
                            f"        {Fore.LIGHTRED_EX}→ Hint: {fail.hint}"
                            f"\n          Args: {fail.kwargs}"
                            f"\n          Failed at: {fail.failed_at}"
                        )

        print()

    def show(self, pipeline: CompletedPipeline) -> None:
        decoration = Fore.WHITE + "-" * 40
        print(f"{decoration}{Fore.CYAN}PIPELINE SUMMARY{Fore.WHITE}{decoration}")

        print(f"{Fore.WHITE}ID: {Fore.GREEN}{pipeline.id}", end="")
        print(
            f"{Fore.WHITE}({pipeline.pipeline_name})" if pipeline.pipeline_name else ""
        )

        print(f"{Fore.WHITE}Sequence: {Fore.GREEN}{pipeline.pipeline_sequence}\n\n")
        print(f"{decoration}{Fore.CYAN}MUTATIONS{Fore.WHITE}{decoration}")

        for index, mutation_data in enumerate(pipeline.pipeline, start=1):
            self.show_mutation(index=index, mutation_data=mutation_data)

        print(f"{decoration}\n")
