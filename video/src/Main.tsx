import React from "react";
import { Audio, Sequence, staticFile } from "remotion";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { S1Hook } from "./scenes/S1Hook";
import { S2Reveal } from "./scenes/S2Reveal";
import { S3Flow } from "./scenes/S3Flow";
import { S4Auto } from "./scenes/S4Auto";
import { S5Export } from "./scenes/S5Export";
import { S6CTA } from "./scenes/S6CTA";

// 旁白音轨：edge-tts 六句解说（public/narration/），每景时长 = 旁白 + 余量
const Vo: React.FC<{ name: string; from?: number }> = ({ name, from = 6 }) => (
  <Sequence from={from} layout="none">
    <Audio src={staticFile(`narration/${name}.mp3`)} />
  </Sequence>
);

// 全 fade 交叉转场 18 帧（勿用 WebGL 着色器/slide，理由见 deep-research-cn video 工程注释）
const t = () => springTiming({ config: { damping: 200, stiffness: 120 }, durationInFrames: 18 });

// 总长 = 1290 - 5×18 = 1200 帧（40.0s）
export const Main: React.FC = () => {
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={240}>
        <S1Hook />
        <Vo name="s1" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={180}>
        <S2Reveal />
        <Vo name="s2" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={195}>
        <S3Flow />
        <Vo name="s3" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={225}>
        <S4Auto />
        <Vo name="s4" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={210}>
        <S5Export />
        <Vo name="s5" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={240}>
        <S6CTA />
        <Vo name="s6" />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
