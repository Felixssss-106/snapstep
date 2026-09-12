import { Config } from "@remotion/cli/config";

// 注意：不要开启 rspack——Windows 无头渲染会报 bundle.js ENOENT
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
