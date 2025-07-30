install
-------
pip3 install quick_qemu


execute
-------

``` sh
python -m quick_qemu <path to cd> <path to image> <argument1> <argument2>...
or
quick_qemu <path to cd> <path to image> <argument1> <argument2>...
```

environment
-----------
* QUICK_QEMU_OUTPUT: set output, default spice-app
* QUICK_QEMU_NOGL: if set disables ql rendering
* QUICK_QEMU_CPU: change virtual cpu
* QUICK_QEMU_MACHINE: change virtual acpi

example
-------

``` sh
python -m quick_qemu ~/Downloads/archlinux.iso

```
