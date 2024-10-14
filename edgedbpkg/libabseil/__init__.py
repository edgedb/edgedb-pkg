from __future__ import annotations

from metapkg import packages
from metapkg import targets


class LibAbseil(packages.BundledCMakePackage):
    title = "libabsl"
    ident = "libabsl"
    aliases = ["libabsl-dev"]

    _server = "https://github.com/abseil/abseil-cpp/archive/"

    sources = [
        {
            "url": _server + "{version}.tar.gz",
        },
    ]

    def get_dep_pkg_name(self) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "ABSL"

    def get_configure_script(self, build: targets.Build) -> str:
        sdir = build.get_source_dir(self, relative_to="pkgbuild")
        sed = build.sh_get_command("sed")
        copts = sdir / "absl/copts/copts.py"

        script = f"""\
        {sed} -i \
            -e '/"-maes",/d' \
            -e '/"-msse4.1",/d' \
            -e '/"-mfpu=neon"/d' \
            -e '/"-march=armv8-a+crypto"/d' \
            "{copts}"
        python3 "{copts}"
        """

        return script + super().get_configure_script(build)

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "-DABSL_ENABLE_INSTALL": "TRUE",
            "-DABSL_USE_EXTERNAL_GOOGLETEST": "ON",
            "-DABSL_PROPAGATE_CXX_STD": "TRUE",
            "-DABSL_BUILD_TEST_HELPERS": "OFF",
            "-DABSL_BUILD_TESTING": "OFF",
        }

    # abseil has ninja-specific hardcode in its CMakeFiles
    def get_target_build_system(
        self,
        build: targets.Build,
    ) -> packages.CMakeTargetBuildSystem:
        return "ninja"

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return [
            "absl_bad_any_cast_impl",
            "absl_bad_optional_access",
            "absl_bad_variant_access",
            "absl_base",
            "absl_city",
            "absl_civil_time",
            "absl_cord",
            "absl_cord_internal",
            "absl_cordz_functions",
            "absl_cordz_handle",
            "absl_cordz_info",
            "absl_cordz_sample_token",
            "absl_crc32c",
            "absl_crc_cord_state",
            "absl_crc_cpu_detect",
            "absl_crc_internal",
            "absl_debugging_internal",
            "absl_demangle_internal",
            "absl_die_if_null",
            "absl_examine_stack",
            "absl_exponential_biased",
            "absl_failure_signal_handler",
            "absl_flags_commandlineflag",
            "absl_flags_commandlineflag_internal",
            "absl_flags_config",
            "absl_flags_internal",
            "absl_flags_marshalling",
            "absl_flags_parse",
            "absl_flags_private_handle_accessor",
            "absl_flags_program_name",
            "absl_flags_reflection",
            "absl_flags_usage",
            "absl_flags_usage_internal",
            "absl_graphcycles_internal",
            "absl_hash",
            "absl_hashtablez_sampler",
            "absl_int128",
            "absl_kernel_timeout_internal",
            "absl_leak_check",
            "absl_log_entry",
            "absl_log_flags",
            "absl_log_globals",
            "absl_log_initialize",
            "absl_log_internal_check_op",
            "absl_log_internal_conditions",
            "absl_log_internal_fnmatch",
            "absl_log_internal_format",
            "absl_log_internal_globals",
            "absl_log_internal_log_sink_set",
            "absl_log_internal_message",
            "absl_log_internal_nullguard",
            "absl_log_internal_proto",
            "absl_log_severity",
            "absl_log_sink",
            "absl_low_level_hash",
            "absl_malloc_internal",
            "absl_periodic_sampler",
            "absl_random_distributions",
            "absl_random_internal_distribution_test_util",
            "absl_random_internal_platform",
            "absl_random_internal_pool_urbg",
            "absl_random_internal_randen",
            "absl_random_internal_randen_hwaes",
            "absl_random_internal_randen_hwaes_impl",
            "absl_random_internal_randen_slow",
            "absl_random_internal_seed_material",
            "absl_random_seed_gen_exception",
            "absl_random_seed_sequences",
            "absl_raw_hash_set",
            "absl_raw_logging_internal",
            "absl_spinlock_wait",
            "absl_stacktrace",
            "absl_status",
            "absl_statusor",
            "absl_str_format_internal",
            "absl_strerror",
            "absl_string_view",
            "absl_strings",
            "absl_strings_internal",
            "absl_symbolize",
            "absl_synchronization",
            "absl_throw_delegate",
            "absl_time",
            "absl_time_zone",
            "absl_vlog_config_internal",
        ]
