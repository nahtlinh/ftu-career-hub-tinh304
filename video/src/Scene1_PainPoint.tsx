import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Scene1_PainPoint: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const typewriterProgress = Math.min(1, frame / (fps * 2));
  const text1 = "You know your FTU major inside out...";
  const charsToShow = Math.floor(text1.length * typewriterProgress);
  const displayedText1 = text1.slice(0, charsToShow);

  const showText2 = frame > fps * 2.5;
  const scaleText2 = spring({
    frame: frame - fps * 2.5,
    fps,
    config: {
      damping: 12,
    },
  });

  const fadeOut = interpolate(frame, [150, 180], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      className="absolute inset-0 flex flex-col items-center justify-center bg-[#0b1c3d]"
      style={{ opacity: fadeOut }}
    >
      <h1 className="text-5xl font-bold text-white text-center mb-8 h-12">
        {displayedText1}
        <span className="animate-pulse">|</span>
      </h1>

      {showText2 && (
        <h2
          className="text-6xl font-extrabold text-[#dc3545] text-center"
          style={{ transform: `scale(${scaleText2})` }}
        >
          But what skills do employers actually want?
        </h2>
      )}
    </div>
  );
};
