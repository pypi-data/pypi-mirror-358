import os

def get_version_from_file():
    version_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "VERSION")
    with open(version_file_path, "r") as fh:
        return fh.read().strip()

def prepare_version():
    version = get_version_from_file()

    branch_name = os.environ.get("CI_COMMIT_BRANCH", "")
    commit_tag = os.environ.get("CI_COMMIT_TAG", "")
    default_branch_name = os.environ.get("CI_DEFAULT_BRANCH", "")

    # if pipeline is not on default or tagged branch, append build id and commit sha
    if branch_name != default_branch_name and not commit_tag:
        build_id = os.environ.get("BUILD_ID", "")
        commit = os.environ.get("BUILD_COMMIT_SHORT_SHA", "")
        version = f"{version}.dev{build_id}+{commit}"

    return version

if __name__ == "__main__":
    print(prepare_version())
