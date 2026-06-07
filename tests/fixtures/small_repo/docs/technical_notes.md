# Technical Notes

## Architecture

The implementation uses locator, foreground extraction, preprocessing, and model inference modules. The architecture documentation describes the interface contract between each stage.

## Runtime

The live runtime supports trace capture by writing trace events for preprocessing and model inference. The runtime configuration is stored in `configs/runtime.yml`.

## Evaluation Protocol

The reported synthetic validation MAE is produced on the synthetic validation split using the documented evaluation protocol. No released checkpoint is included in this fixture.

## Incident Review

Failures were investigated with trace-backed incident analysis notes and linked review notes.

## Scope Notes

The documentation states that this is not intended to be a general-purpose monocular 3D vision system.

