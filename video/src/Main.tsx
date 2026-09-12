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
    <Audio src={staticFile(`narration/${name}.wav`)} />
  </Sequence>
);

// 全 fade 交叉转场 18 帧（勿用 WebGL 着色器/slide，理由见 deep-research-cn video 工程注释）
const t = () => springTiming({ config: { damping: 200, stiffness: 120 }, durationInFrames: 18 });

// 总长 = 1290 - 5×18 = 1200 帧（40.0s）
// 苏打（MiMo-V2.5-TTS）旁白实测：6.08/5.44/7.52/8.96/6.72/8.16s
// 各景 = max(节拍下限, ceil((旁白+1.0s)*30/15)*15)；总长 = 1500 - 5×18 = 1410 帧（47.0s）
export const Main: React.FC = () => {
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={225}>
        <S1Hook />
        <Vo name="s1" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={195}>
        <S2Reveal />
        <Vo name="s2" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={255}>
        <S3Flow />
        <Vo name="s3" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={300}>
        <S4Auto />
        <Vo name="s4" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={240}>
        <S5Export />
        <Vo name="s5" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={285}>
        <S6CTA />
        <Vo name="s6" />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
