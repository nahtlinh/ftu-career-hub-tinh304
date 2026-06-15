import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

export const Scene3_MarketInsight: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animations
  const fade = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: 'clamp'
  });
  
  const contentFade = interpolate(frame, [15, 30], [0, 1], {
    extrapolateRight: 'clamp'
  });
  const contentSlide = spring({ frame: frame - 15, fps, config: { damping: 14 } });

  const jobsCount = Math.floor(
    interpolate(frame, [40, 70], [0, 15], { extrapolateRight: "clamp", extrapolateLeft: "clamp" })
  );

  const skills = [
    { name: "Excel", jobs: 8, maxJobs: 10 },
    { name: "Giao Tiếp", jobs: 6, maxJobs: 10 },
    { name: "Tiếng Anh", jobs: 2, maxJobs: 10 },
    { name: "Làm Việc Nhóm", jobs: 2, maxJobs: 10 },
  ];

  return (
    <div className="absolute inset-0 bg-white flex flex-col font-sans overflow-hidden" style={{ opacity: fade }}>
      {/* Navbar */}
      <div className="h-[72px] bg-white border-b border-gray-100 flex items-center justify-between px-12 z-50 w-full shadow-sm shrink-0">
        <div className="flex items-center gap-1">
          <div className="w-10 h-10 bg-[#15294e] rounded-full flex items-center justify-center text-white text-xl font-black">
            C
          </div>
          <span className="text-[#dc3545] text-[22px] font-bold tracking-tight">areerHub</span>
        </div>
        
        <div className="flex gap-10">
          <span className="text-gray-500 font-semibold text-[15px] pt-6">Trang chủ</span>
          <span className="text-gray-500 font-semibold text-[15px] pt-6">Việc làm</span>
          <span className="text-[#dc3545] font-bold text-[15px] border-b-[3px] border-[#dc3545] pb-6 pt-6">Market Insight</span>
          <span className="text-gray-500 font-semibold text-[15px] pt-6">Hồ sơ</span>
        </div>

        <div className="flex items-center gap-6">
          <svg className="text-gray-500 w-[22px] h-[22px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
          <svg className="text-gray-500 w-[22px] h-[22px]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          <div className="w-[34px] h-[34px] border border-[#dc3545] rounded-full flex items-center justify-center text-[#dc3545] font-bold text-sm">
            G
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex justify-center items-start pt-12 bg-[#fafbfc]">
        <div 
          className="w-[850px] bg-white rounded-xl shadow-[0_2px_10px_rgba(0,0,0,0.05)] border border-gray-100 p-10"
          style={{ opacity: contentFade, transform: `translateY(${(1 - contentSlide) * 40}px)` }}
        >
           {/* Dropdown & Button */}
           <div className="flex gap-4 mb-8">
             <div className="flex-1 border border-gray-300 rounded-md p-3 flex justify-between items-center text-[#212529] font-medium text-[15px]">
               Tài chính (Finance)
               <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
             </div>
             <button className="bg-[#dc3545] text-white px-8 py-3 rounded-md font-bold text-[15px]">Tra cứu</button>
           </div>

           {/* Header */}
           <div className="mb-8">
             <h2 className="text-[#dc3545] text-[24px] font-bold mb-1">Insight: Ngành Finance</h2>
             <p className="text-gray-500 text-[14px]">Dữ liệu thị trường thời gian thực được trích xuất từ hàng ngàn tin tuyển dụng.</p>
           </div>

           {/* Summary Cards */}
           <div className="flex gap-6 mb-10">
             <div className="flex-1 bg-gray-50 border border-gray-100 rounded-xl py-6 text-center flex flex-col items-center justify-center">
               <p className="text-[#212529] font-bold text-[14px] mb-2">Số lượng Jobs Mở</p>
               <p className="text-[#dc3545] text-[32px] font-bold">
                 {jobsCount > 0 ? jobsCount : ""}
                 {jobsCount === 0 && <span className="opacity-0">0</span> /* Layout placeholder */}
               </p>
             </div>
             <div className="flex-1 bg-gray-50 border border-gray-100 rounded-xl py-6 text-center flex flex-col items-center justify-center">
               <p className="text-[#212529] font-bold text-[14px] mb-2">Mức lương TB (Triệu VNĐ)</p>
               <p className="text-[#0d6efd] text-[24px] font-bold mt-1">Đang cập nhật</p>
             </div>
           </div>

           {/* Top Skills Chart */}
           <div>
             <h3 className="font-bold text-[#212529] text-[16px] mb-4">Top Kỹ năng Yêu cầu</h3>
             <div className="border-t border-gray-100 pt-5 flex flex-col gap-4">
               {skills.map((skill, index) => {
                 const barWidth = spring({
                   frame: frame - 60 - index * 10,
                   fps,
                   config: { damping: 12 },
                 });
                 const targetPercent = (skill.jobs / skill.maxJobs) * 100;
                 return (
                   <div key={skill.name} className="flex items-center gap-4">
                     <span className="w-28 text-right text-[13px] font-bold text-[#212529] shrink-0">{skill.name}</span>
                     <div className="flex-1 h-7 bg-gray-100 rounded-md overflow-hidden relative">
                       <div 
                         className="h-full bg-[#0d6efd] rounded-md flex items-center px-3"
                         style={{ width: `${Math.max(barWidth * targetPercent, 10)}%` }}
                       >
                         <span className="text-white text-[12px] font-bold whitespace-nowrap" style={{ opacity: barWidth }}>{skill.jobs} jobs</span>
                       </div>
                     </div>
                   </div>
                 );
               })}
             </div>
           </div>

        </div>
      </div>
    </div>
  );
};
