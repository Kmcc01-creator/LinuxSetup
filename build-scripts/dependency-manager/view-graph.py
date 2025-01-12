graph TD
    %% Core Modules
    GraphicsCore[Graphics Core]
    MathCore[Math Core]
    Utils[Utils]

    %% Graphics Submodules
    Renderers[Renderers]
    Shaders[Shaders]
    Scene[Scene Graph]
    Primitives[Primitives]

    %% Math Submodules
    Linear[Linear Algebra]
    Geometry[Geometry]
    Algorithms[Math Algorithms]

    %% Utility Submodules
    Logging[Logging System]
    Errors[Error Handling]
    Config[Configuration]

    %% External Dependencies
    PyOpenGL[PyOpenGL]
    Vulkan[Vulkan]
    Numpy[NumPy]
    Scipy[SciPy]
    Cython[Cython]
    PDM[PDM]

    %% Graphics Dependencies
    GraphicsCore --> Renderers
    GraphicsCore --> Shaders
    GraphicsCore --> Scene
    GraphicsCore --> Primitives
    
    Renderers --> PyOpenGL
    Renderers --> Vulkan
    Renderers --> Linear
    Renderers --> Geometry
    
    Shaders --> Linear
    Shaders --> Cython
    
    Scene --> Geometry
    Scene --> Algorithms
    
    Primitives --> Geometry
    Primitives --> Linear

    %% Math Dependencies
    MathCore --> Linear
    MathCore --> Geometry
    MathCore --> Algorithms
    
    Linear --> Numpy
    Algorithms --> Scipy
    Algorithms --> Numpy
    
    %% Utility Dependencies
    Utils --> Logging
    Utils --> Errors
    Utils --> Config
    
    %% Cross-module Dependencies
    GraphicsCore --> Utils
    MathCore --> Utils
    
    %% Build System
    PDM --> GraphicsCore
    PDM --> MathCore
    PDM --> Utils

    %% Error and Logging Integration
    Renderers --> Errors
    Shaders --> Errors
    Scene --> Errors
    Linear --> Errors
    Geometry --> Errors
    Algorithms --> Errors
    
    %% Style
    classDef core fill:#f9f,stroke:#333,stroke-width:2px
    classDef external fill:#bbf,stroke:#333,stroke-width:1px
    classDef util fill:#bfb,stroke:#333,stroke-width:1px
    
    class GraphicsCore,MathCore core
    class PyOpenGL,Vulkan,Numpy,Scipy,Cython,PDM external
    class Utils,Logging,Errors,Config util