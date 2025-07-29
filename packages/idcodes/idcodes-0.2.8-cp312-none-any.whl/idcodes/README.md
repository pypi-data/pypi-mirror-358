# Pybind11 Idcodes API

## Build & Installation

### 1. Create Virtual Environment 

```bash
# We are using python 3.12
python3 -m venv .venv
source .venv/bin/activate
# Install requirements to build package
pip install -r requirements.txt
pip install -r idcodes/requirements.txt
```

### 3. Build Project

Navigate to idcodes project directory and follow the steps.
```bash
1. To configure current Preset run: 
    ```bash
    cmake --preset <buildPresets.name>
    ```
2. To build run:
    ```bash
    cmake --build --preset <buildPresets.name>
    ```
3. To install run:
    ```bash
    cmake --build --target install --preset <buildPresets.name> 
```

### 4. Verify `.so` file and copy to python environment
Copy the .so file to your virtual environment's site-packages directory:

```bash
       
       # Uninstall old version of idcodeslibrary if exists
       sudo apt remove idcodeslibrary

        ```bash

       # Download the `*.deb` package and install it using `dpkg`
       sudo dpkg -i idcodeslibrary_*.deb
       # If you encounter any dependency issues, you can resolve them by running:
       sudo apt-get install -f
       
        # Verify by searching for installed packages
        dpkg -l | grep -i idcodes


       # Modify or update idcodeslibrary.conf file to add `/usr/local/lib` to path
       sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/idcodeslibrary.conf'
       # verify the contents of the file
       cat /etc/ld.so.conf.d/idcodeslibrary.conf

       # Configure
       sudo ldconfig

       # Verify if *.so files for idcodes library are in path
       ldconfig -p | grep -i idcodes

```

- **Create a Virtual Environment**  
    It is recommended to use a virtual environment to isolate the dependencies for the project. Run the following command to create a virtual environment:

    ```
         sudo apt install python3-venv
         python3.12 -m venv .venv
         python -m pip install --upgrade pip
    ```
- **Activate the Virtual Environment**  
    Activate the virtual environment using the following command:

    ```
         source .venv/bin/activate
         python -m pip install --upgrade pip
    ```
- **Generate Python Wheel for idcodes pybind API**
    ```bash
        python -m build
        # This will generate *.whl package in `dist` folder
    ```
- **Install the Package**  
    Once the virtual environment is activated, install the `idcodes` `*.whl` using the provided wheel file:

    ```
         pip install ./dist/idcodes-xx_xx_xx-cp312-cp312-linux_xx_xx.whl
    ```
- **Verify the Installation**  
    After installation, you can verify that the package is installed correctly by running:

    ```
         python -c "import idcodes; print(dir(idcodes))"
    ```
    If the package is installed correctly, you should see the message:  
    `idcodes installed successfully!`


### 5. Test the Module

```bash
python
>>> import idcodes
>>> print(dir(idcodes))
```


### 6. Build, package and Install the Project

Run the following commands to build and install the project:

```bash
# From idcodes directory folder
python -m build
pip install dist/*.whl
```
### 7. Uninstall .whl Package 

Run the following commands to uninstall the project:

```bash
pip uninstall dist/*.whl
```

## Notes

- Ensure that all dependencies are installed before building the project.
- Use a virtual environment to avoid conflicts with system-wide packages.
- Refer to the official Pybind11 and CMake documentation for advanced configuration options.


```bash
    pip install myst-parser
```

for latex pdf
```bash
    sudo apt install texlive-full 
```

