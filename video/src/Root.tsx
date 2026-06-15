import { Composition } from "remotion";
import { MainVideo } from "./MainVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="FTUCareerHubSaaS"
        component={MainVideo}
        durationInFrames={810}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
