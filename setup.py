from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="RLP_TMR2023",
        version="0.0.1",
        url="https://github.com/AgustinZavalaA/RLP_TMR2023",
        author="Agustin Zavala",
        author_email="1930120@upv.edu.mx",
        description="Team Prosito code repository for Beach Cleaning Robot for the Mexican Robotics Tournament 2023.",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
    )
