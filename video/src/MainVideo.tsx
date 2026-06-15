import { Series, Audio, staticFile } from "remotion";
import { Scene0_Homepage } from "./Scene0_Homepage";
import { Scene2_FTUProfile } from "./Scene2_FTUProfile";
import { Scene3_MarketInsight } from "./Scene3_MarketInsight";
import { Scene4_SkillMatchOutro } from "./Scene4_SkillMatchOutro";
import { Scene5_Outro } from "./Scene5_Outro";

export const MainVideo: React.FC = () => {
  return (
    <div className="flex-1 bg-white">
      {/* Âm thanh nền và Voiceover từ thư mục public */}
      <Audio src={staticFile("bg.mp3")} volume={0.3} />
      <Audio src={staticFile("voice.mp3")} />
      
      <Series>
        {/* Scene 0: 6s */}
        <Series.Sequence durationInFrames={180}>
          <Scene0_Homepage />
        </Series.Sequence>

        {/* Scene 3: 5s */}
        <Series.Sequence durationInFrames={150}>
          <Scene3_MarketInsight />
        </Series.Sequence>

        {/* Scene 2: 4s */}
        <Series.Sequence durationInFrames={120}>
          <Scene2_FTUProfile />
        </Series.Sequence>

        {/* Scene 4: 6s */}
        <Series.Sequence durationInFrames={180}>
          <Scene4_SkillMatchOutro />
        </Series.Sequence>

        {/* Scene 5 (Outro): 6s */}
        <Series.Sequence durationInFrames={180}>
          <Scene5_Outro />
        </Series.Sequence>
      </Series>
    </div>
  );
};
