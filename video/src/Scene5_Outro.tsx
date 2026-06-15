import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig, Img, staticFile } from 'remotion';

export const Scene5_Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoScale = spring({
    frame: frame - 15,
    fps,
    config: { damping: 12 },
  });

  const textOpacity = interpolate(frame, [45, 75], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const textY = interpolate(frame, [45, 75], [30, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div className="absolute inset-0 bg-[#0b1c3d] flex flex-col items-center justify-center font-sans overflow-hidden">
      <div style={{ transform: `scale(${logoScale})` }} className="flex flex-col items-center mb-12">
        <div className="w-36 h-36 bg-white rounded-3xl flex items-center justify-center p-4 shadow-2xl mb-8">
          <Img src={staticFile("logo.png")} className="w-full h-full object-contain" />
        </div>
        <h1 className="text-white text-[56px] font-black tracking-tight">FTU Career Hub</h1>
      </div>

      <div 
        className="flex flex-col items-center text-center px-12"
        style={{ opacity: textOpacity, transform: `translateY(${textY}px)` }}
      >
        <h2 className="text-[#dc3545] text-[36px] font-bold mb-4">
          Nâng tầm kỹ năng, Rộng mở cơ hội nghề nghiệp.
        </h2>
        <p className="text-gray-300 text-[26px] font-semibold border-t border-gray-600 pt-6 mt-4 inline-block px-12">
          Trải nghiệm ngay hôm nay!
        </p>
      </div>
    </div>
  );
};
