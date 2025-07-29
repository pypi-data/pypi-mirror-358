"""Python bindings for OPSIN using JPype."""

import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Union

try:
    import jpype
    import jpype.imports
except ImportError as e:
    raise ImportError(
        "JPype is required. Please install it with 'pip install JPype1'"
    ) from e

from .exceptions import OpsinJVMError

if TYPE_CHECKING:
    from uk.ac.cam.ch.wwmm.opsin import NameToStructureConfig


class OpsinPy:
    """Python bindings for OPSIN using JPype for direct Java integration.

    This class provides a high-performance interface to OPSIN by directly
    calling Java methods without subprocess overhead.
    """

    def __init__(self, jar_path: Optional[str] = None):
        """Initialize the OPSIN Python interface.

        Args:
            jar_path: Path to OPSIN JAR file. If None, uses bundled JAR.
        """
        self._jar_path = jar_path or self._get_default_jar_path()
        self._jvm_started = False
        self._name_to_structure = None
        self._name_to_inchi = None

        # Verify JAR file exists
        if not os.path.exists(self._jar_path):
            raise OpsinJVMError(f"OPSIN JAR file not found: {self._jar_path}")

    def _get_default_jar_path(self) -> str:
        """Get path to bundled OPSIN JAR file."""
        try:
            try:
                from importlib.resources import files

                return str(
                    files("opsinpy") / "opsin-cli-2.8.0-jar-with-dependencies.jar"
                )
            except ImportError:
                from pkg_resources import resource_filename

                return resource_filename(  # type: ignore[no-any-return,has-type]
                    "opsinpy", "opsin-cli-2.8.0-jar-with-dependencies.jar"
                )
        except Exception:
            # Fallback to relative path
            current_dir = Path(__file__).parent
            jar_path = current_dir / "opsin-cli-2.8.0-jar-with-dependencies.jar"
            return str(jar_path)

    def _start_jvm(self) -> None:
        """Start JVM and initialize OPSIN classes."""
        if self._jvm_started:
            return

        try:
            # Check if JVM is already started by another instance
            if jpype.isJVMStarted():
                warnings.warn(
                    "JVM already started. Using existing JVM instance.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            else:
                # Start JVM with OPSIN JAR in classpath
                jpype.startJVM(classpath=[self._jar_path])

            # Import OPSIN classes
            from uk.ac.cam.ch.wwmm.opsin import (
                NameToInchi,
                NameToStructure,
                NameToStructureConfig,
                OpsinResult,
            )

            # Initialize OPSIN instances
            self._name_to_structure = NameToStructure.getInstance()
            self._name_to_structure_config_class = NameToStructureConfig
            self._name_to_inchi_class = NameToInchi
            self._opsin_result_class = OpsinResult

            self._jvm_started = True

        except Exception as e:
            raise OpsinJVMError(f"Failed to start JVM or initialize OPSIN: {e}") from e

    def _create_config(
        self,
        allow_acids_without_acid: bool = False,
        allow_radicals: bool = False,
        allow_uninterpretable_stereo: bool = False,
        detailed_failure_analysis: bool = False,
    ) -> "NameToStructureConfig":
        """Create OPSIN configuration object with specified options."""
        self._start_jvm()

        config = self._name_to_structure_config_class()
        config.setInterpretAcidsWithoutTheWordAcid(allow_acids_without_acid)
        config.setAllowRadicals(allow_radicals)
        config.setWarnRatherThanFailOnUninterpretableStereochemistry(
            allow_uninterpretable_stereo
        )
        config.setDetailedFailureAnalysis(detailed_failure_analysis)

        return config

    def _convert_single_name(
        self, name: str, output_format: str, config: "NameToStructureConfig"
    ) -> Optional[str]:
        """Convert a single chemical name to the specified format."""
        try:
            # Parse the chemical name
            opsin_result = self._name_to_structure.parseChemicalName(name, config)

            # Check if parsing was successful
            if (
                opsin_result.getStatus()
                == self._opsin_result_class.OPSIN_RESULT_STATUS.FAILURE
            ):
                message = str(opsin_result.getMessage())
                if message:
                    warnings.warn(
                        f"Failed to parse '{name}': {message}",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                return None

            # Get output in requested format
            format_upper = output_format.upper()

            result = None
            if format_upper == "SMILES":
                result = opsin_result.getSmiles()
            elif format_upper == "EXTENDEDSMILES":
                result = opsin_result.getExtendedSmiles()
            elif format_upper == "CML":
                result = opsin_result.getCml()
            elif format_upper == "INCHI":
                result = self._name_to_inchi_class.convertResultToInChI(opsin_result)
            elif format_upper == "STDINCHI":
                result = self._name_to_inchi_class.convertResultToStdInChI(opsin_result)
            elif format_upper == "STDINCHIKEY":
                result = self._name_to_inchi_class.convertResultToStdInChIKey(
                    opsin_result
                )
            else:
                raise ValueError(f"Unsupported output format: {output_format}")

            return str(result) if result is not None else None

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            warnings.warn(
                f"Error converting '{name}': {e}", RuntimeWarning, stacklevel=2
            )
            return None

    def convert(
        self,
        chemical_name: Union[str, List[str]],
        output_format: str = "SMILES",
        **options: Any,
    ) -> Union[str, List[Optional[str]], None]:
        """Convert chemical name(s) to specified format.

        Args:
            chemical_name: Single chemical name or list of names
            output_format: Output format ("SMILES", "ExtendedSMILES", "CML", "InChI", "StdInChI", "StdInChIKey")
            **options: OPSIN configuration options

        Returns:
            Converted structure(s) or None if conversion fails
        """
        self._start_jvm()

        # Handle single name vs list
        is_single = isinstance(chemical_name, str)
        names = [chemical_name] if is_single else chemical_name

        config = self._create_config(**options)
        results = []

        for name in names:
            result = self._convert_single_name(name, output_format, config)  # type: ignore[arg-type]
            results.append(result)

        return results[0] if is_single else results

    # Convenience methods for different output formats
    def name_to_smiles(self, name: str, **options: Any) -> Optional[str]:
        """Convert chemical name to SMILES."""
        result = self.convert(name, "SMILES", **options)
        return result if isinstance(result, str) else None

    def name_to_extended_smiles(self, name: str, **options: Any) -> Optional[str]:
        """Convert chemical name to Extended SMILES."""
        result = self.convert(name, "ExtendedSMILES", **options)
        return result if isinstance(result, str) else None

    def name_to_cml(self, name: str, **options: Any) -> Optional[str]:
        """Convert chemical name to CML."""
        result = self.convert(name, "CML", **options)
        return result if isinstance(result, str) else None

    def name_to_inchi(self, name: str, **options: Any) -> Optional[str]:
        """Convert chemical name to InChI."""
        result = self.convert(name, "InChI", **options)
        return result if isinstance(result, str) else None

    def name_to_stdinchi(self, name: str, **options: Any) -> Optional[str]:
        """Convert chemical name to StdInChI."""
        result = self.convert(name, "StdInChI", **options)
        return result if isinstance(result, str) else None

    def name_to_stdinchikey(self, name: str, **options: Any) -> Optional[str]:
        """Convert chemical name to StdInChIKey."""
        result = self.convert(name, "StdInChIKey", **options)
        return result if isinstance(result, str) else None

    # Batch conversion methods
    def names_to_smiles(self, names: List[str], **options: Any) -> List[Optional[str]]:
        """Convert list of chemical names to SMILES."""
        result = self.convert(names, "SMILES", **options)
        return result if isinstance(result, list) else [None] * len(names)

    def names_to_extended_smiles(
        self, names: List[str], **options: Any
    ) -> List[Optional[str]]:
        """Convert list of chemical names to Extended SMILES."""
        result = self.convert(names, "ExtendedSMILES", **options)
        return result if isinstance(result, list) else [None] * len(names)

    def names_to_cml(self, names: List[str], **options: Any) -> List[Optional[str]]:
        """Convert list of chemical names to CML."""
        result = self.convert(names, "CML", **options)
        return result if isinstance(result, list) else [None] * len(names)

    def names_to_inchi(self, names: List[str], **options: Any) -> List[Optional[str]]:
        """Convert list of chemical names to InChI."""
        result = self.convert(names, "InChI", **options)
        return result if isinstance(result, list) else [None] * len(names)

    def names_to_stdinchi(
        self, names: List[str], **options: Any
    ) -> List[Optional[str]]:
        """Convert list of chemical names to StdInChI."""
        result = self.convert(names, "StdInChI", **options)
        return result if isinstance(result, list) else [None] * len(names)

    def names_to_stdinchikey(
        self, names: List[str], **options: Any
    ) -> List[Optional[str]]:
        """Convert list of chemical names to StdInChIKey."""
        result = self.convert(names, "StdInChIKey", **options)
        return result if isinstance(result, list) else [None] * len(names)

    def __del__(self) -> None:
        """Cleanup - note that JVM shutdown is handled globally by JPype."""
        # JPype handles JVM lifecycle, so we don't need to explicitly shut it down
        pass

    @staticmethod
    def shutdown_jvm() -> None:
        """Manually shutdown the JVM.

        Note: This will affect all JPype-based applications in the process.
        Use with caution.
        """
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
