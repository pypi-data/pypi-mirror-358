import subprocess

class ManagerInstall:

    @staticmethod
    def install_requirements(
        requirements_file="requirements.txt", failed_file="failed_requirements.txt"):
        failed_packages = []
        # open requirements.txt and read module name
        with open(requirements_file, "r") as file:
            packages = file.readlines()

        # iterate each package name and try to install
        for package in packages:
            package = package.strip()

            if package:  # skip empty line
                print(f"installing: {package}")
                try:
                    # use subprocess to execute pip install command
                    result = subprocess.run(
                        ["pip", "install", package],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )

                    # check install result, if return code is not 0, then install failed
                    if result.returncode != 0:
                        print(f"install failed: {package}")

                        failed_packages.append(package)

                except Exception as e:
                    print(f"error: {e}")
                    failed_packages.append(package)

        # write failed packages to failed_requirements.txt
        if failed_packages:
            cleaned_lines = []
            for line in failed_packages:
                # remove version part (==后面的内容)
                package = line.split("==")[0].strip()
                if package:  # skip empty line
                    cleaned_lines.append(package)
            with open(failed_file, "w") as f:
                f.write("\n".join(cleaned_lines))
            print(f"install failed packages to {failed_file}")
            return False
        else:
            print("all packages installed successfully")
            return True


    @staticmethod
    def install(            
        requirements_file="requirements.txt",
        failed_file="failed_requirements.txt",
        retry=2,
    ):
        for i in range(retry):
            print(f"retry {i+1} of {retry}")
            if i == 0:
                continue_install = ManagerInstall.install_requirements(
                    requirements_file, failed_file
                )
            else:
                continue_install = ManagerInstall.install_requirements(
                    failed_file, failed_file
                )
            if continue_install:
                break
        return continue_install

if __name__ == "__main__":
    ManagerInstall.install()

