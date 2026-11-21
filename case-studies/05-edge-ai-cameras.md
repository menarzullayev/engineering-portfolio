# Edge-AI firmware and model conversion for smart cameras

> Status: employer work at TassVision, private. No code, customer names, addresses or internal documents appear here, only what I am allowed to say about the shape of the work. The scale figure is approved for publication by me as the author. Written 2026-11-22.

| | |
|---|---|
| **Role** | Engineer in the firmware and AI models team since December 2025, after an internship (September to November 2025). I work with a colleague. |
| **Stack** | C++17, CMake, Ambarella CV25 (CNNGen toolchain), ONNX, TypeScript, ClickHouse |
| **Scope** | On-camera detection, tracking and line-crossing events; conversion of face-recognition models to the camera's binary format; fleet analytics |
| **Scale** | About 1,950 devices were live in the 7 days before 2026-11-06 |

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tassvision-edge-ai-dark.svg"><img src="../assets/tassvision-edge-ai-light.svg" alt="Edge-AI cameras: ONNX model, model conversion, camera firmware, platform requests, camera events and fleet analytics" width="100%"></picture>

## What the work is

Smart cameras run their models on the device. That moves three jobs to us: getting a model onto the camera's accelerator in the format it needs, writing the firmware that runs detection and tracking and turns them into events (for example a person crossing a line), and understanding from the other end how the whole fleet behaves.

- **Firmware.** C++17 for the Ambarella CV25: detection, tracking and line-crossing events.
- **Model conversion.** Face-recognition models start as ONNX files and are converted with the vendor toolchain (CNNGen) into the binary the camera loads.
- **Fleet analytics.** TypeScript tooling over the fleet's request data in ClickHouse, used to see how the fleet behaves, including how many devices are active.

## How the device count is made

The figure on this page is a count of devices that sent at least one request to the platform inside a window. It was taken on 2026-11-06 from the fleet's request logs: about 1,950 devices in the preceding 7 days. It says that many devices were reachable and talking. It does not say how many were doing useful work, how many customers there are, or how accurate the models were.

## What I do not publish

- Accuracy numbers for the models. I do not have field accuracy to publish, and a number measured on a different set of images would mislead.
- Customer names, store names, addresses or any footage.
- Internal tooling, repository names and the vendor's toolchain files (they are licensed, not mine).

## Decisions

### Run detection and tracking on the camera, keep fleet analysis on the server

- **Decision:** detection, tracking and line-crossing events run on the camera's accelerator. The server receives events and request data, and fleet analysis happens there.
- **Why (as I understand it):** two reasons. Latency and traffic: sending every video stream to a server costs bandwidth and adds delay, while an event is a few bytes. Cost at scale: with about 1,950 devices active in a week, running every stream through server-side models would need far more compute than the cameras' own accelerators, which are already paid for.
- **Whose decision and when:** inherited architecture. It was in place before I joined (internship started September 2025), so I did not make it. I work inside it and I know its reasons from the team, not from a design document I can cite.
- **Source:** my own account as the author. No public document backs it, and I have not measured the alternative (server-side inference), so the cost reasoning is not a number I can show.
- **What it costs:** every model must fit the camera's accelerator and be converted to its binary format, which is the model-conversion work above. A model that does not convert cleanly cannot ship.

### Write the firmware in C++17, built with CMake

- **Decision:** the on-camera firmware is C++17 and is built with CMake.
- **Why (as I understand it):** three reasons. The vendor toolchain for the CV25 expects it, so another language is not a realistic option. The camera has limited memory and CPU and the detection and tracking loop is real-time, which favours a language with manual memory control and low overhead. C++17 specifically, not a newer standard, because the camera toolchain's compiler supports up to that level.
- **Whose decision and when:** inherited. It was already in place before I joined (internship started September 2025). I did not choose it and I have no design document to cite.
- **Source:** my own account as the author. I have not compared it against another language on this hardware.
- **What it costs:** I cannot use language features newer than C++17, and the build has to follow what the vendor toolchain accepts.

### Convert models with the vendor toolchain only, quantised with calibration, and check the result

- **Decision:** a model goes from ONNX to the camera's binary format through the vendor's CNNGen toolchain and nothing else. It is quantised (INT8) using a calibration set, and the converted model's output is checked against the original ONNX before it is used.
- **Why (as I understand it):** the camera's accelerator only loads the vendor's format, so there is no second route to compare. Quantisation is needed to run on the accelerator, and calibration is what keeps the quantised model close to the original. The check exists because a conversion can finish without errors and still change the model's behaviour.
- **Whose decision and when:** inherited. The process was already in place before I joined (internship started September 2025). I follow it and I have no design document to cite.
- **Source:** my own account as the author. I do not publish the size of the differences the check finds (see the accuracy point above).
- **What it costs:** a model that the toolchain cannot convert cannot ship, however good it is in ONNX. Calibration needs a representative image set, and a poor set gives a worse model.

## What is not done on this page

- Only three decisions are listed so far. More will be added only when I can state each with a date and a source.
- The number above is a snapshot. The fleet changes daily; this page does not.
