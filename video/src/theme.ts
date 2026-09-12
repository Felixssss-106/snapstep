// 深色开发者工具风设计系统（与 deep-research-cn 视频同系，品牌强调色改为 SnapStep 红）
export const C = {
  bg: "#0D1117",
  bgDeep: "#010409",
  panel: "#161B22",
  border: "#30363D",
  text: "#E6EDF3",
  dim: "#8B949E",
  green: "#3FB950",
  red: "#F85149", // SnapStep 品牌色：步骤高亮圈同款红
  amber: "#D29922",
  term: "#7EE787",
} as const;

export const FONT_CN = '"Noto Sans SC", "Microsoft YaHei", sans-serif';
export const FONT_MONO = '"JetBrains Mono", Consolas, monospace';

export const EASE_EXPO = [0.16, 1, 0.3, 1] as [number, number, number, number];

// 各分镜帧数（30fps）
export const SCENE_FRAMES = {
  S1: 240,
  S2: 180,
  S3: 195,
  S4: 225,
  S5: 195,
  S6: 240,
} as const;
