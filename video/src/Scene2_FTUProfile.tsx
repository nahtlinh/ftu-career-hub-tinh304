import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { MousePointer2 } from "lucide-react";

export const Scene2_FTUProfile: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideIn = spring({
    frame,
    fps,
    config: { damping: 14 },
  });

  const cursorX = interpolate(frame, [30, 60], [1400, 1250], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cursorY = interpolate(frame, [30, 60], [800, 480], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const clickScale = spring({
    frame: frame - 60,
    fps,
    config: { damping: 10, mass: 0.5 },
  });

  const showDropdown = frame > 65;
  
  const cursorX2 = interpolate(frame, [70, 90], [1250, 960], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cursorY2 = interpolate(frame, [70, 90], [480, 560], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const clickScale2 = spring({
    frame: frame - 90,
    fps,
    config: { damping: 10, mass: 0.5 },
  });

  const showTags = frame > 95;

  const tags = ["Data Analysis", "Python", "Marketing", "English", "Logistics"];

  return (
    <div className="absolute inset-0 bg-[#f8f9fa] flex items-center justify-center font-sans">
      <div
        className="w-[800px] bg-white rounded-xl shadow-lg border border-gray-100 p-8 relative"
        style={{ transform: `translateY(${(1 - slideIn) * 100}px)`, opacity: slideIn }}
      >
        <div className="absolute top-4 right-4 bg-[#dc3545] text-white text-xs font-bold px-2 py-1 rounded">
          FTU Exclusive
        </div>
        <h2 className="text-2xl font-bold text-[#0b1c3d] mb-6">Setup Profile</h2>
        
        <div className="mb-6 relative">
          <label className="block text-sm font-semibold text-gray-600 mb-2">Select FTU Major</label>
          <div className="w-full border border-gray-300 rounded-lg p-3 text-gray-800 bg-gray-50 flex justify-between items-center">
            <span>{showTags ? "Kinh tế đối ngoại (Foreign Trade)" : "Select a major..."}</span>
            <span className="text-gray-400">▼</span>
          </div>
          
          {showDropdown && !showTags && (
            <div className="absolute top-full left-0 w-full bg-white border border-gray-200 mt-1 rounded-lg shadow-xl z-10 overflow-hidden">
              <div className="p-3 hover:bg-gray-100 cursor-pointer text-gray-800 border-b border-gray-100">Khoa học máy tính</div>
              <div className="p-3 hover:bg-gray-100 cursor-pointer text-gray-800 border-b border-gray-100">Tài chính Ngân hàng</div>
              <div className="p-3 bg-gray-50 cursor-pointer font-bold text-[#dc3545] border-b border-gray-100">Kinh tế đối ngoại</div>
              <div className="p-3 hover:bg-gray-100 cursor-pointer text-gray-800">Kinh doanh quốc tế</div>
            </div>
          )}
        </div>

        <div className="min-h-[120px]">
          <label className="block text-sm font-semibold text-gray-600 mb-2">Auto-Extracted Skills</label>
          <div className="flex flex-wrap gap-2">
            {showTags &&
              tags.map((tag, i) => {
                const tagScale = spring({
                  frame: frame - 95 - i * 5,
                  fps,
                  config: { damping: 12 },
                });
                return (
                  <span
                    key={tag}
                    className="bg-red-50 text-[#dc3545] border border-red-200 px-4 py-2 rounded-full text-sm font-bold"
                    style={{ transform: `scale(${tagScale})` }}
                  >
                    {tag}
                  </span>
                );
              })}
            {!showTags && <span className="text-gray-400 italic text-sm">Skills will appear here...</span>}
          </div>
        </div>

      </div>

      {/* Cursor */}
      <div
        className="absolute z-50 text-black drop-shadow-md"
        style={{
          left: frame < 70 ? cursorX : cursorX2,
          top: frame < 70 ? cursorY : cursorY2,
          transform: `scale(${frame > 90 ? 1 - clickScale2 * 0.2 : frame > 60 ? 1 - clickScale * 0.2 : 1})`,
        }}
      >
        <MousePointer2 fill="black" size={32} />
      </div>
      
      {/* Overlay Text */}
      <div 
        className="absolute bottom-12 w-full text-center"
        style={{ opacity: interpolate(frame, [150, 180], [0, 1]) }}
      >
        <h1 className="text-4xl font-extrabold text-[#0b1c3d]">Auto-extract skills instantly.</h1>
      </div>
    </div>
  );
};
