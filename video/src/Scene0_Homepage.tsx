import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, Img, staticFile } from 'remotion';

export const Scene0_Homepage: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Scroll down animation starting from frame 40 to 120
  const scrollY = interpolate(frame, [40, 120], [0, -1450], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp'
  });

  const fade = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: 'clamp'
  });

  // Mock Data
  const categories = [
    { name: "IT / Phần mềm", color: "bg-blue-100 text-blue-600", icon: "M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" },
    { name: "Tài chính / Đầu tư", color: "bg-green-100 text-green-600", icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
    { name: "Marketing / PR", color: "bg-purple-100 text-purple-600", icon: "M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" },
    { name: "Kế toán / Kiểm toán", color: "bg-yellow-100 text-yellow-600", icon: "M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
    { name: "Logistics", color: "bg-orange-100 text-orange-600", icon: "M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" },
    { name: "Nhân sự", color: "bg-teal-100 text-teal-600", icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" },
    { name: "Kinh doanh", color: "bg-red-100 text-red-600", icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" },
    { name: "Ngân hàng", color: "bg-cyan-100 text-cyan-600", icon: "M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" }
  ];

  const courses = [
    { title: "ACCA Qualification", org: "BISC", logo: "logos/bisc.jpg" },
    { title: "Khóa học Acca Hoc Thu", org: "BISC", logo: "logos/bisc.jpg" },
    { title: "ACCA Online", org: "BISC", logo: "logos/bisc.jpg" },
    { title: "ACCA Offline", org: "BISC", logo: "logos/bisc.jpg" },
    { title: "Power BI", org: "Datapot", logo: "logos/datapot.png" },
    { title: "Khóa học Da 100 Analyzing Data With Power Bi", org: "Datapot", logo: "logos/datapot.png" },
    { title: "Khóa học AI Marketing Sales System", org: "Tomorrow Marketers", logo: "logos/tomorrow_marketers.jpg" },
    { title: "Data System", org: "Tomorrow Marketers", logo: "logos/tomorrow_marketers.jpg" },
    { title: "Google Data Analytics", org: "Coursera", logo: "" },
    { title: "Business Analysis", org: "MindX", logo: "" },
    { title: "Data Analysis For Business", org: "UniTrain", logo: "logos/unitrain.png" },
  ];

  return (
    <div className="absolute inset-0 bg-white flex flex-col font-sans overflow-hidden" style={{ opacity: fade }}>
      {/* Navbar (Fixed) */}
      <div className="h-[72px] bg-white border-b border-gray-100 flex items-center justify-between px-12 z-50 absolute top-0 w-full shadow-sm">
        <div className="flex items-center gap-1">
          <div className="w-10 h-10 bg-[#15294e] rounded-full flex items-center justify-center text-white text-xl font-black">
            C
          </div>
          <span className="text-[#dc3545] text-[22px] font-bold tracking-tight">areerHub</span>
        </div>
        
        <div className="flex gap-10">
          <span className="text-[#dc3545] font-bold text-[15px] border-b-[3px] border-[#dc3545] pb-6 pt-6">Trang chủ</span>
          <span className="text-gray-500 font-semibold text-[15px] pt-6">Việc làm</span>
          <span className="text-gray-500 font-semibold text-[15px] pt-6">Market Insight</span>
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

      {/* Scrollable Content */}
      <div className="absolute top-[72px] w-full" style={{ transform: `translateY(${scrollY}px)` }}>
        
        {/* Hero Banner */}
        <div className="px-8 py-6">
          <div className="bg-[#15294e] rounded-xl text-center py-28 px-8 shadow-md">
             <h1 className="text-white text-[56px] font-extrabold mb-6 tracking-tight">Looking for your best-fit job?</h1>
             <p className="text-gray-200 mb-10 text-[19px]">Type your keyword, then click search to find your perfect job.</p>
             
             <div className="flex justify-center mb-8">
               <div className="flex w-[860px] gap-3">
                 <input 
                   type="text" 
                   className="flex-1 bg-white rounded-lg px-6 py-[18px] text-[17px] outline-none text-gray-800 placeholder-gray-500 font-medium shadow-sm" 
                   placeholder="Tìm kiếm vị trí, công ty hoặc kỹ năng..." 
                   readOnly
                 />
                 <button className="bg-[#dc3545] text-white px-10 py-[18px] rounded-lg font-bold text-[17px] shadow-sm">
                   Tìm việc ngay
                 </button>
               </div>
             </div>

             <div className="flex justify-center gap-4">
               <button className="border border-gray-400 text-white px-8 py-2.5 rounded-md text-[15px] font-semibold hover:bg-white hover:text-[#15294e] transition">
                 Khám phá việc làm
               </button>
               <button className="bg-white text-[#15294e] px-10 py-2.5 rounded-md text-[15px] font-bold shadow-md">
                 Profile
               </button>
               <button className="border border-gray-400 text-white px-8 py-2.5 rounded-md text-[15px] font-semibold hover:bg-white hover:text-[#15294e] transition">
                 Market Insight
               </button>
             </div>
          </div>
        </div>

        {/* Categories Section */}
        <div className="pt-8 pb-12 text-center bg-white px-12 max-w-7xl mx-auto">
          <h2 className="text-[32px] font-extrabold text-[#212529] mb-3 tracking-tight">Ngành nghề phổ biến</h2>
          <p className="text-gray-500 mb-10 text-[17px]">Khám phá các vị trí thực tập theo lĩnh vực bạn yêu thích</p>
          
          <div className="grid grid-cols-4 gap-6">
            {categories.map((cat, i) => (
              <div key={i} className="h-[140px] bg-white border border-gray-200 shadow-sm hover:shadow-md hover:border-blue-200 rounded-xl flex flex-col items-center justify-center transition-all cursor-pointer group">
                 <div className={`w-14 h-14 ${cat.color} rounded-xl mb-3 flex items-center justify-center group-hover:scale-110 transition-transform`}>
                   <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={cat.icon}></path>
                   </svg>
                 </div>
                 <span className="text-[#212529] font-bold text-[15px]">{cat.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Courses Section */}
        <div className="py-16 bg-white px-12 pb-24">
          <div className="max-w-7xl mx-auto">
            
            <div className="text-center mb-10">
              <h2 className="text-[36px] font-extrabold text-[#15294e] mb-2 tracking-tight">Khóa học đề xuất</h2>
              <p className="text-[#0d6efd] text-[18px] uppercase tracking-wide font-medium">DÀNH CHO SINH VIÊN</p>
            </div>
            
            <div className="grid grid-cols-4 gap-4">
              {courses.map((course, i) => (
                <div key={i} className="bg-white rounded-[10px] border border-gray-200 shadow-sm hover:shadow-md p-5 flex flex-col justify-between h-[155px] cursor-pointer transition-shadow">
                   
                   <div>
                      <div className="flex gap-3 items-start mb-3">
                         <div className={`w-8 h-8 rounded shrink-0 shadow-sm overflow-hidden flex items-center justify-center bg-white border border-gray-100`}>
                           <Img src={staticFile(course.logo)} className="w-full h-full object-contain" />
                         </div>
                         <h3 className="font-extrabold text-[#212529] text-[15px] leading-snug line-clamp-2">
                           {course.title}
                         </h3>
                      </div>
                      <p className="text-[13px] text-gray-500">Trung tâm: <span className="text-gray-600 font-medium">{course.org}</span></p>
                   </div>

                   <div className="text-right mt-2">
                      <span className="text-[#0d6efd] text-[13px] font-semibold hover:underline">Tìm hiểu thêm &gt;</span>
                   </div>

                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
