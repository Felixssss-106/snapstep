import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT_MONO } from "../theme";

// 终端窗体：三色圆点 + 标题栏 + 等宽正文区
export const Terminal: React.FC<{
  title?: string;
  width?: number | string;
  style?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ title = "zcode — 终端", width = 900, style, bodyStyle, children }) => {
  return (
    <div
      style={{
        width,
        background: C.bgDeep,
        border: `1px solid ${C.border}`,
        borderRadius: 12,
        overflow: "hidden",
        boxShadow: "0 24px 80px rgba(0,0,0,0.55)",
        ...style,
      }}
    >
      <div
        style={{
          height: 44,
          background: C.panel,
          borderBottom: `1px solid ${C.border}`,
          display: "flex",
          alignItems: "center",
          paddingLeft: 16,
          position: "relative",
        }}
      >
        <div style={{ display: "flex", gap: 8 }}>
          {["#FF5F56", "#FFBD2E", "#27C93F"].map((c) => (
            <div
              key={c}
              style={{ width: 12, height: 12, borderRadius: 6, background: c }}
            />
          ))}
        </div>
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            textAlign: "center",
            fontFamily: FONT_MONO,
            fontSize: 16,
            color: C.dim,
          }}
        >
          {title}
        </div>
      </div>
      <div
        style={{
          padding: "26px 30px",
          fontFamily: FONT_MONO,
          fontSize: 22,
          lineHeight: "42px",
          color: C.text,
          ...bodyStyle,
        }}
      >
        {children}
      </div>
    </div>
  );
};

// 终端行：from 帧起逐字打出，占位高度固定保证版面稳定
export const TLine: React.FC<{
  from: number;
  text: string;
  color?: string;
  framesPerChar?: number;
  height?: number;
}> = ({ from, text, color = C.text, framesPerChar = 1.2, height = 42 }) => {
  const frame = useCurrentFrame();
  const n = Math.max(0, Math.floor((frame - from) / framesPerChar));
  const shown = text.slice(0, Math.min(n, text.length));
  const typing = n > 0 && n < text.length;
  return (
    <div style={{ height, whiteSpace: "pre", color, display: "flex", alignItems: "center", gap: 12 }}>
      <span>{shown}</span>
      {typing ? (
        <span style={{ opacity: frame % 8 < 4 ? 1 : 0, color: C.term }}>▍</span>
      ) : null}
    </div>
  );
};
