import React from "react";
import { C } from "../theme";

// SnapStep 品牌图标：红色高亮圈 + 序号角标（呼应产品给每次点击画的标注）
export const SnapLogo: React.FC<{ size?: number }> = ({ size = 120 }) => (
  <svg width={size} height={size} viewBox="0 0 96 96" fill="none">
    <circle cx={42} cy={54} r={26} stroke={C.red} strokeWidth={7} fill="none" />
    <circle cx={42} cy={54} r={7} fill={C.red} opacity={0.35} />
    <rect x={58} y={10} width={28} height={28} rx={14} fill={C.red} />
    <text
      x={72}
      y={30}
      fontSize={19}
      fontWeight={700}
      fill="#FFFFFF"
      textAnchor="middle"
      fontFamily="JetBrains Mono, monospace"
    >
      1
    </text>
  </svg>
);
