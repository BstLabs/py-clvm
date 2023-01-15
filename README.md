# <div align="center"><b>CLVM</b></div>

[![Downloads](https://static.pepy.tech/personalized-badge/pyclvm?period=total&units=none&left_color=orange&right_color=blue&left_text=Downloads)](https://pepy.tech/project/pyclvm)
[![](https://img.shields.io/pypi/v/pyclvm?label=PyPi)](https://pypi.org/project/pyclvm/)
[![](https://img.shields.io/github/license/BstLabs/py-clvm?color=blue&label=License)](https://github.com/BstLabs/py-clvm/blob/main/LICENSE.md)
[![Changelog](https://github.com/BstLabs/py-clvm/workflows/Changelog/badge.svg)](https://github.com/BstLabs/py-clvm/blob/main/CHANGELOG.md)
[![Lint](https://github.com/BstLabs/py-clvm/actions/workflows/lint.yml/badge.svg)](https://github.com/BstLabs/py-clvm/actions/workflows/lint.yml)
[![Type](https://github.com/BstLabs/py-clvm/actions/workflows/type.yml/badge.svg)](https://github.com/BstLabs/py-clvm/actions/workflows/type.yml)


A Cloud VM command line tool for powerful and efficient management of cloud instances

This tool addresses the inefficient hassle of having to use your mouse to click lots of buttons to start/stop instances and configure and use these cloud services via a web interface. This is an unproductive way to work. If you use VSCode Remote or port redirection to access your cloud instance resources, then the steps are doubled.

To improve the development experience, we have replicated various solutions for handling different steps of using cloud virtual machines and combined them with VSCode Remote to deliver maximum convenience for fellow developers and engineers.

CLVM currently works with cloud instances on AWS, Azure and GCP. It is built on top of [DynaCLI](https://github.com/BstLabs/py-dynacli), another excellent open-source tool from [BST Labs](https://github.com/BstLabs/). For more detail on using CLVM, see the blog post [Simplify Cloud Instance Management from your Command Line](https://medium.com/@orkhanshirin/simplify-cloud-instance-management-from-your-command-line-4b44a5b3949e).

## Capabilities of CLVM

1. Instance start/stop and listing operations
2. SSH key generation and tunneling
3. Session management
4. Port redirection (forwarding)
5. VSCode Remote utilities
6. Support for AWS, GCP, and, Azure

## Installation

`$ pip3 install pyclvm`

## Quick start

*Each cloud platform can require different authorization procedures. For detailed authorization information please check the respective provider's documentation.*

```console
$ clvm ssh new <vm_instance_name> platform=<aws, gcp or azure>
```
```console
$ clvm vscode start <vm_instance_name>
```

## How to install for local development

`$ flit install --symlink`

This will give you `clvm` command installed.

## Some Useful Tools

[ssh-over-ssm](https://github.com/elpy1/ssh-over-ssm)

[ssm-tools](https://github.com/mludvig/aws-ssm-tools)

[vscode remote over ssm](https://github.com/aws/aws-toolkit-vscode/issues/941)

[aws-mfa](https://github.com/broamski/aws-mfa)
