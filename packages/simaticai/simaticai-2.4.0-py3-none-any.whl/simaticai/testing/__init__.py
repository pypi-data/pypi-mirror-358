# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
## Test pipeline configuration package locally

When you have created your inference pipeline package, you could go straight on with deploying it to the AI Inference Server.
**However, we strongly recommend that you test your package before you deploy it.**
The benefits of local testing are the following:

- You can figure out many potential problems quicker, as you don't have to go through a deployment cycle.
- You can diagnose and troubleshoot issues more easily, as you can inspect artifacts in your development environment.
- You can validate your fixes quicker and move on to further issues that have not surfaced yet due to earlier issues.
- You can easily include the local pipeline tests into the test automation in your build process.

In general, we encourage you to apply state-of-the-art software engineering practices, such as unit testing and test driven development.
This means that ideally you already have automated unit or even integration tests in place that make sure that the Python code and the
saved models work according to expectations in isolation. This helps you localize errors when you put these pieces together and integrate
them as a pipeline configuration package.

AI SDK package `simaticai.testing` provides two tools for local testing:

- A pipeline validator, that performs a static validation of the package concerning the availability of required
Python packages.
- A pipeline runner, that lets you simulate the execution of your pipeline in your Python environment.

Please note that all this functionality applies to pipeline configuration packages, not edge configuration packages. In other words,
you must use them before you convert your pipeline configuration package to an edge configuration package using the `convert_package` function.
As the conversion itself is done in an automated way, most potential problems are already present in the package
before the conversion, so a verification after conversion would only delay identifying these problems.

For more comprehensive guidance on how to test pipelines before deployment, we recommend you refer to
the AI SDK User Manual, especially the chapter concerning local testing of pipeline configuration packages.
We also recommend you study the project templates for the AI SDK, which provide concrete code examples that show how to feed a pipeline with different
kinds of inputs in a local test.
"""

from .pipeline_runner import LocalPipelineRunner
from .component_runner import ComponentRunner

__all__ = [
    "LocalPipelineRunner", 
    "ComponentRunner"]
