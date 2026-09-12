import React from "react";
import { Composition, Folder } from "remotion";
import { loadFont as loadNotoSansSC } from "@remotion/google-fonts/NotoSansSC";
import { loadFont as loadJetBrainsMono } from "@remotion/google-fonts/JetBrainsMono";
import { Main } from "./Main";
import { S1Hook } from "./scenes/S1Hook";
import { S2Reveal } from "./scenes/S2Reveal";
import { S3Flow } from "./scenes/S3Flow";
import { S4Auto } from "./scenes/S4Auto";
import { S5Export } from "./scenes/S5Export";
import { S6CTA } from "./scenes/S6CTA";
import { Cover } from "./scenes/Cover";

// 中文与等宽字体，避免渲染机缺字回退
loadNotoSansSC("normal", { weights: ["400", "500", "700"] });
loadJetBrainsMono("normal", { weights: ["400", "700"], subsets: ["latin"] });

const V = {
  fps: 30,
  width: 1920,
  height: 1080,
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="分镜">
        <Composition id="S1Hook" component={S1Hook} durationInFrames={225} {...V} />
        <Composition id="S2Reveal" component={S2Reveal} durationInFrames={195} {...V} />
        <Composition id="S3Flow" component={S3Flow} durationInFrames={255} {...V} />
        <Composition id="S4Auto" component={S4Auto} durationInFrames={300} {...V} />
        <Composition id="S5Export" component={S5Export} durationInFrames={240} {...V} />
        <Composition id="S6CTA" component={S6CTA} durationInFrames={285} {...V} />
      </Folder>

      <Composition id="Main" component={Main} durationInFrames={1410} {...V} />
      <Composition
        id="Cover"
        component={Cover}
        durationInFrames={1}
        fps={30}
        width={1280}
        height={720}
      />
    </>
  );
};
