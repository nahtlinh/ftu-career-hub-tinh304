import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const Scene4_SkillMatchOutro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const circleProgress = spring({
    frame: frame - 10,
    fps,
    config: { damping: 20 },
  });
  const matchScore = Math.floor(circleProgress * 92);

  const showExisting = frame > 20;
  const showMissing = frame > 30;
  const showCourse = frame > 45;

  const showButton = frame > 60;
  const buttonScale = spring({
    frame: frame - 60,
    fps,
    config: { damping: 10, mass: 0.8 },
  });

  return (
    <div className="absolute inset-0 bg-[#f8f9fa] flex items-center justify-center font-sans overflow-hidden">
      
      {/* Skill Match Phase */}
      <div className="flex flex-col w-full max-w-5xl bg-white rounded-xl shadow-2xl overflow-hidden relative">
        {/* Job Details Card matching the web UI */}
          
          {/* Blue Banner */}
          <div className="bg-[#0b5ed7] h-36 w-full flex justify-center pt-8">
            <h1 className="text-white text-[28px] font-black uppercase tracking-[0.2em]">Grow Together</h1>
          </div>
          
          {/* Job Header (Overlapping) */}
          <div className="bg-white mx-8 -mt-12 rounded-xl shadow-lg border border-gray-100 p-6 flex justify-between items-center z-10 relative">
             <div className="flex items-center gap-6">
               <div className="w-16 h-16 flex items-center justify-center text-[#0b1c3d] font-black text-2xl bg-gray-50 rounded-lg border border-gray-200">
                 C
               </div>
               <div className="flex flex-col gap-1">
                 <h2 className="text-xl font-extrabold text-[#212529]">Finance Data Analyst Executive</h2>
                 <p className="text-sm text-gray-500">https://talent.urbox.vn/</p>
                 <p className="text-sm text-gray-500 font-medium">FULL-TIME | Hà Nội | <span className="text-[#dc3545] font-bold">20.000.000 - 25.000.000 VNĐ</span></p>
               </div>
             </div>
             <div style={{ transform: `scale(${buttonScale})` }}>
               <button className="bg-[#ef4444] hover:bg-[#dc2626] text-white px-8 py-3 rounded-lg font-bold shadow-md transition-colors">
                 Apply Now
               </button>
             </div>
          </div>

          {/* Tabs */}
          <div className="px-8 mt-6 border-b border-gray-200 flex gap-8">
            <span className="text-[15px] font-semibold text-gray-400 pb-3">Job Details</span>
            <span className="text-[15px] font-semibold text-gray-400 pb-3">Company Overview</span>
            <span className="text-[15px] font-bold text-[#212529] pb-3 border-b-[3px] border-[#dc3545]">Skill Match Analysis</span>
          </div>

          {/* Tab Content (Skill Match) */}
          <div className="p-8 flex gap-12">
            
            {/* Left: Circle Score */}
            <div className="flex flex-col items-center justify-center w-1/3 border-r border-gray-100 pr-8">
              <div className="relative w-40 h-40 mb-2">
                <svg className="w-full h-full transform -rotate-90 drop-shadow-sm" viewBox="0 0 100 100">
                  <circle
                    className="text-gray-100 stroke-current"
                    strokeWidth="12"
                    cx="50"
                    cy="50"
                    r="40"
                    fill="transparent"
                  ></circle>
                  <circle
                    className="text-[#fbbf24] stroke-current"
                    strokeWidth="12"
                    strokeLinecap="round"
                    cx="50"
                    cy="50"
                    r="40"
                    fill="transparent"
                    strokeDasharray="251.2"
                    strokeDashoffset={251.2 - (251.2 * matchScore) / 100}
                  ></circle>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center flex-col">
                  <span className="text-[32px] font-black text-[#212529]">{matchScore}%</span>
                </div>
              </div>
            </div>

            {/* Right: Skills & Courses */}
            <div className="flex flex-col flex-1 justify-center gap-6">
              
              <div style={{ opacity: showExisting ? 1 : 0, transition: 'opacity 0.3s' }}>
                <h4 className="flex items-center text-[15px] font-bold text-[#212529] mb-3">
                  Kỹ năng đã có <svg className="w-[18px] h-[18px] text-[#10b981] ml-2" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"></path></svg>
                </h4>
                <div className="flex flex-wrap gap-2">
                  {["Data Analysis", "Strategic Planning", "Data Analysis / Phân tích dữ liệu"].map((skill, i) => {
                    const scale = spring({
                      frame: frame - 20 - i * 5,
                      fps,
                      config: { damping: 12 },
                    });
                    return (
                      <span 
                        key={skill} 
                        className="bg-[#d1fae5] text-[#059669] px-4 py-2 rounded-full text-xs font-bold border border-[#a7f3d0]"
                        style={{ transform: `scale(${scale})` }}
                      >
                        {skill.toUpperCase()}
                      </span>
                    );
                  })}
                </div>
              </div>

              <div style={{ opacity: showMissing ? 1 : 0, transition: 'opacity 0.3s' }}>
                <h4 className="flex items-center text-[15px] font-bold text-[#212529] mb-3">
                  Kỹ năng còn thiếu <svg className="w-[18px] h-[18px] text-[#ef4444] ml-2" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z"></path></svg>
                </h4>
                <div className="flex gap-2">
                  {["Power BI", "Finance Modeling"].map((skill, i) => {
                    const scale = spring({
                      frame: frame - 30 - i * 5,
                      fps,
                      config: { damping: 12 },
                    });
                    return (
                      <span 
                        key={skill} 
                        className="bg-[#fee2e2] text-[#dc2626] px-4 py-2 rounded-full text-xs font-bold border border-[#fecaca]"
                        style={{ transform: `scale(${scale})` }}
                      >
                        {skill.toUpperCase()}
                      </span>
                    );
                  })}
                </div>
              </div>

              <div 
                style={{ 
                  opacity: showCourse ? 1 : 0, 
                  transform: `scale(${spring({ frame: frame - 45, fps, config: { damping: 14 } })})`,
                  transformOrigin: 'top left'
                }}
                className="mt-2"
              >
                <h4 className="text-[15px] font-bold text-[#1e293b] mb-3 border-b-[3px] border-[#1e293b] inline-block pb-1">
                  Khóa học thực chiến (Trung tâm ngoài)
                </h4>
                <div className="bg-white border-l-[6px] border-[#1e293b] border-t border-r border-b border-gray-100 p-4 rounded-r-lg shadow-sm">
                  <h5 className="font-bold text-[#1e293b] text-sm mb-1">Khóa học Power BI thực chiến</h5>
                  <p className="text-xs text-gray-500 mb-3">Trung tâm: <span className="font-bold text-gray-700">Datapot</span></p>
                  <span className="bg-[#1e293b] text-white px-3 py-1.5 rounded-md text-[11px] font-bold tracking-wide uppercase">
                    Tìm hiểu thêm ↗
                  </span>
                </div>
              </div>

            </div>

          </div>
        </div>

    </div>
  );
};
