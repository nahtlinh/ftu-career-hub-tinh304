// Global State
let currentUser = null;
let currentProfile = { name: '', dob: '', major: '', skills: [] };
let jobsData = [];
let affiliateCourses = [];
let ftuCourses = [];
let externalCourses = [];

document.addEventListener('DOMContentLoaded', async () => {
    initNavigation();
    initMockFirebase();
    loadProfileState(); // Load profile from local storage
    await loadInitialData();
    
    // Setup Search & Filter Listeners
    const searchInput = document.getElementById('job-search');
    if (searchInput) searchInput.addEventListener('input', renderJobList);
    
    const categoryInput = document.getElementById('job-category');
    if (categoryInput) categoryInput.addEventListener('change', renderJobList);

    // Bind custom skill addition
    const addSkillBtn = document.getElementById('add-skill-btn');
    const customSkillInput = document.getElementById('custom-skill-input');
    if (addSkillBtn && customSkillInput) {
        addSkillBtn.addEventListener('click', () => {
            const newSkill = customSkillInput.value.trim().toLowerCase();
            if (newSkill) {
                if (!currentProfile.skills.includes(newSkill)) {
                    currentProfile.skills.push(newSkill);
                    renderProfileForm();
                    customSkillInput.value = '';
                } else {
                    alert('Kỹ năng này đã tồn tại trong hồ sơ!');
                }
            }
        });
        
        customSkillInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addSkillBtn.click();
            }
        });
    }

    // Bind Edit Profile button
    const editProfileBtn = document.getElementById('edit-profile-btn');
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', () => {
            switchToView('profile-view');
        });
    }
});

// --- Navigation ---
function switchToView(viewId) {
    const views = document.querySelectorAll('.view-section');
    views.forEach(view => {
        if (view.id === viewId) view.classList.remove('hidden');
        else view.classList.add('hidden');
    });
    
    // Update active nav-item
    document.querySelectorAll('.nav-item').forEach(nav => {
        const target = nav.getAttribute('data-target');
        if (target === viewId || (target === 'profile-view' && viewId === 'profile-dashboard-view')) {
            nav.classList.add('active');
        } else {
            nav.classList.remove('active');
        }
    });

    if (viewId === 'profile-view') {
        renderProfileForm();
    } else if (viewId === 'profile-dashboard-view') {
        populateDashboard();
    }
}

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item, .nav-trigger');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('data-target');
            
            // Check if redirect is needed for profile
            if (targetId === 'profile-view' && currentProfile && currentProfile.major) {
                switchToView('profile-dashboard-view');
            } else {
                switchToView(targetId);
            }
        });
    });
    
    // Industry Cards Click -> Insights
    document.querySelectorAll('.industry-card').forEach(card => {
        card.addEventListener('click', () => {
            const industry = card.getAttribute('data-industry');
            showInsights(industry);
            
            // Switch view
            switchToView('insights-view');
            
            // Set insights-view select value
            const select = document.getElementById('insight-industry-select');
            if (select) select.value = industry;
        });
    });
    
    // Home search click -> Jobs
    const btnSearch = document.getElementById('btn-hero-search');
    if (btnSearch) {
        btnSearch.addEventListener('click', () => {
            switchToView('jobs-view');
        });
    }

    // Logo Click -> Home
    const navLogo = document.getElementById('nav-logo');
    if (navLogo) {
        navLogo.addEventListener('click', () => {
            switchToView('home-view');
        });
    }

    // Avatar Click -> Auth Modal
    const userAvatarBtn = document.getElementById('user-avatar-btn');
    const authModal = document.getElementById('auth-modal');
    if (userAvatarBtn && authModal) {
        userAvatarBtn.addEventListener('click', () => {
            authModal.classList.remove('hidden');
        });
    }

    const closeAuthBtn = document.getElementById('close-auth-modal');
    if (closeAuthBtn) {
        closeAuthBtn.addEventListener('click', () => {
            authModal.classList.add('hidden');
        });
    }

    // Insight Dropdown changes
    const insightSelect = document.getElementById('insight-industry-select');
    const btnInsight = document.getElementById('btn-insight-search');
    if (btnInsight && insightSelect) {
        btnInsight.addEventListener('click', () => {
            if (insightSelect.value) {
                showInsights(insightSelect.value);
            }
        });
        insightSelect.addEventListener('change', () => {
            showInsights(insightSelect.value);
        });
    }
}

// --- Firebase Mock & Auth ---
function initMockFirebase() {
    const authModal = document.getElementById('auth-modal');

    const googleBtn = document.getElementById('google-login-btn');
    if (googleBtn) {
        googleBtn.addEventListener('click', () => {
            currentUser = { uid: "123", email: "user@gmail.com", displayName: "Người dùng FTU" };
            if(authModal) authModal.classList.add('hidden');
            onLoginSuccess();
        });
    }

    const manualBtn = document.getElementById('manual-login-btn');
    if (manualBtn) {
        manualBtn.addEventListener('click', () => {
            currentUser = { uid: "guest", email: "guest@ftu.edu.vn", displayName: "Khách" };
            if(authModal) authModal.classList.add('hidden');
            onLoginSuccess();
        });
    }
}

function loadProfileState() {
    const savedProfile = localStorage.getItem('careerHubProfile');
    const savedUser = localStorage.getItem('careerHubUser');
    
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        document.getElementById('user-avatar-btn').innerHTML = `<div class="avatar-placeholder">G</div>`;
    }
    
    if (savedProfile) {
        currentProfile = JSON.parse(savedProfile);
    }
}

function onLoginSuccess() {
    localStorage.setItem('careerHubUser', JSON.stringify(currentUser));
    document.getElementById('user-avatar-btn').innerHTML = `<div class="avatar-placeholder">G</div>`;
    
    // If profile is already setup, go to dashboard or jobs, else go to setup
    if (currentProfile && currentProfile.major) {
        document.querySelector('[data-target="profile-dashboard-view"]').click();
    } else {
        document.querySelector('[data-target="profile-view"]').click();
    }
}

let rawInsightsData = null;

// --- Load Data ---
async function loadInitialData() {
    try {
        // Load App Data (Market insights, courses, categories)
        const response = await fetch('data/app_data.json');
        const data = await response.json();
        
        if (data.market_insights) {
            rawInsightsData = data.market_insights;
        }
        
        // Load ftu courses and external courses
        if (data.ftu_courses) {
            ftuCourses = data.ftu_courses;
        }
        if (data.external_courses) {
            externalCourses = data.external_courses;
        }
        
        // Load Affiliate Courses
        try {
            const courseRes = await fetch('data/affiliate_courses.json');
            affiliateCourses = await courseRes.json();
            renderHomeCourses();
        } catch(err) {
            console.log("Could not load affiliate courses JSON.");
        }
        
        // Assign jobs list from backend export
        if(data.jobs && data.jobs.length > 0) {
            jobsData = data.jobs;
        } else {
            // Fallback if empty
            jobsData = [];
        }

        renderJobList();
        populateMajorDropdown();
    } catch (e) {
        console.error("Error loading data:", e);
    }
}

function renderHomeCourses() {
    const grid = document.getElementById('home-courses-grid');
    if(!grid) return;
    
    grid.innerHTML = '';
    
    // Add mock courses for UniTrain and Tomorrow Marketers since they might be missing in JSON
    const additionalCourses = [
        { title: "Ứng dụng Excel trong Kế toán", provider: "UniTrain", category: "Excel", url: "https://unitrain.edu.vn/khoa-hoc/ung-dung-excel-trong-ke-toan/" },
        { title: "Tổ chức dữ liệu & Lập BCTC bằng Excel", provider: "UniTrain", category: "Excel", url: "https://unitrain.edu.vn/khoa-hoc/to-chuc-du-lieu-va-lap-bctc-bang-excel/" },
        { title: "Dashboard Reporting in Excel", provider: "UniTrain", category: "Excel", url: "https://unitrain.edu.vn/khoa-hoc/dashboard-reporting-in-excel/" },
        { title: "Data System in Marketing", provider: "Tomorrow Marketers", category: "Marketing", url: "https://www.tomorrowmarketers.org/khoa-hoc-data-system-in-marketing" },
        { title: "Digital Performance Marketing", provider: "Tomorrow Marketers", category: "Marketing", url: "https://www.tomorrowmarketers.org/khoa-hoc-digital-performance-marketing" }
    ];
    
    const allCourses = [...affiliateCourses, ...additionalCourses];

    const getCourses = (keyword, count) => {
        return allCourses.filter(c => c.title.toLowerCase().includes(keyword.toLowerCase()) || (c.category && c.category.toLowerCase().includes(keyword.toLowerCase()))).slice(0, count);
    };

    // Pick 4 of each requested category to make a 4x4 grid (16 items)
    const displayCourses = [
        ...getCourses("acca", 4),
        ...getCourses("excel", 4),
        ...getCourses("power bi", 4),
        ...getCourses("marketing", 4)
    ];

    displayCourses.forEach(c => {
        const logoFile = c.provider === 'BISC' ? 'bisc.jpg' :
                         c.provider === 'Datapot' ? 'datapot.png' :
                         c.provider === 'Tomorrow Marketers' ? 'tomorrow_marketers.jpg' :
                         c.provider === 'UniTrain' ? 'unitrain.png' : '';
                         
        const cleanTitle = c.title.split('?')[0];
        
        grid.innerHTML += `
            <div class="industry-card course-item" style="text-align: left; display: flex; flex-direction: column;">
                <div style="display:flex; align-items:center; margin-bottom:8px;">
                    ${logoFile ? `<img src="logos/${logoFile}" alt="${c.provider}" style="height:28px; width:auto; margin-right:12px; border-radius: 4px; border: 1px solid #e9ecef;">` : ''}
                    <h3 style="color: #212529; font-size: 16px; margin:0; line-height: 1.4;">${cleanTitle}</h3>
                </div>
                <p style="color: #6c757d; font-size: 14px; margin-bottom: 16px;">Trung tâm: ${c.provider}</p>
                <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: auto;">
                    <a href="${c.url}" target="_blank" style="color: #007bff; text-decoration: none; font-weight: 500;">Tìm hiểu thêm ></a>
                </div>
            </div>
        `;
    });
}

function renderProfileForm() {
    if (!currentProfile) return;
    
    const nameInput = document.getElementById('profile-name');
    if (nameInput) nameInput.value = currentProfile.name || (currentUser ? currentUser.displayName : '');
    
    const dobInput = document.getElementById('profile-dob');
    if (dobInput) dobInput.value = currentProfile.dob || '';
    
    const majorSelect = document.getElementById('profile-major');
    if (majorSelect) majorSelect.value = currentProfile.major || '';
    
    // Populate tags
    if (currentProfile.major) {
        // Extract major skills map
        const majorSkillsMap = {
            "Kinh doanh quốc tế": ["Presentation", "Market Research", "Data Analysis", "Logistics", "Strategic Planning", "Negotiation", "Supply Chain", "English", "Communication"],
            "Khoa học máy tính": ["Python", "SQL", "C++", "Algorithm", "Database", "Machine Learning", "System Design", "Agile", "Scrum", "Git"],
            "Kinh tế đối ngoại": ["Communication", "English", "Negotiation", "Excel", "International Trade", "Import/Export", "Market Research", "Logistics"],
            "Quản trị kinh doanh": ["Management", "Leadership", "Excel", "Communication", "Agile", "Strategic Planning", "Operations", "Finance Basics", "Marketing Basics"],
            "Marketing": ["SEO", "Content Creation", "Communication", "Creativity", "Market Research", "Google Analytics", "Digital Marketing", "Copywriting", "Campaign Management"],
            "Tài chính-Ngân hàng": ["Excel", "Finance", "Analytical Skills", "PowerBI", "Risk Management", "Investment", "Accounting Basics", "SQL"]
        };
        const majorSkills = majorSkillsMap[currentProfile.major] || ["Excel", "Communication", "Teamwork", "Problem Solving", "Presentation", "Time Management", "Critical Thinking"];
        
        // Show major tags (only those that are still in currentProfile.skills)
        const visibleMajorSkills = majorSkills.filter(s => currentProfile.skills.includes(s.toLowerCase()));
        renderTags('major-tags', visibleMajorSkills, true);
        
        // Show CV tags (skills in currentProfile.skills that are NOT in majorSkills)
        const cvSkills = currentProfile.skills.filter(s => !majorSkills.map(ms => ms.toLowerCase()).includes(s));
        renderTags('cv-tags', cvSkills, true);
    } else {
        document.getElementById('major-tags').innerHTML = '<span class="empty-tag-msg">Vui lòng chọn chuyên ngành...</span>';
        document.getElementById('cv-tags').innerHTML = '<span class="empty-tag-msg">Chưa tải CV...</span>';
    }
}

function populateDashboard() {
    const nameEl = document.getElementById('profile-name') ? document.getElementById('profile-name').value : '';
    const displayName = nameEl || currentProfile.name || (currentUser ? currentUser.displayName : "Người dùng");
    
    const nameText = document.getElementById('dash-user-name');
    if (nameText) nameText.textContent = displayName;
    
    const avatarText = document.getElementById('dash-avatar-text');
    if (avatarText) avatarText.textContent = displayName.charAt(0).toUpperCase();
    
    const majorText = document.getElementById('dash-user-major');
    if (majorText) majorText.textContent = currentProfile.major || "Chưa chọn chuyên ngành";

    // Populate Dashboard Skills
    const skillsEl = document.getElementById('dash-user-skills');
    if (skillsEl) {
        skillsEl.innerHTML = '';
        if (currentProfile.skills && currentProfile.skills.length > 0) {
            currentProfile.skills.forEach(s => {
                const tag = document.createElement('span');
                tag.className = 'tag';
                tag.textContent = s.toUpperCase();
                skillsEl.appendChild(tag);
            });
        } else {
            skillsEl.innerHTML = '<span style="color: var(--text-secondary); font-style: italic;">Chưa thiết lập kỹ năng</span>';
        }
    }
    
    // Populate Dummy Saved Courses & Jobs
    const recentJobsEl = document.getElementById('dash-recent-jobs');
    const savedCoursesEl = document.getElementById('dash-saved-courses');
    
    if (recentJobsEl) {
        if (jobsData && jobsData.length > 0) {
            recentJobsEl.innerHTML = jobsData.slice(0, 3).map(job => `
                <div style="display: flex; gap: 12px; align-items: center; border-bottom: 1px solid #e9ecef; padding-bottom: 12px;">
                    <div style="width: 40px; height: 40px; background: #eee; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #555;">${job.company ? job.company.charAt(0).toUpperCase() : 'C'}</div>
                    <div>
                        <h4 style="font-size: 14px; margin-bottom: 4px; color: #333;">${job.title}</h4>
                        <p style="font-size: 12px; color: #777;">${job.company}</p>
                    </div>
                </div>
            `).join('');
        } else {
            recentJobsEl.innerHTML = '<p style="color: var(--text-secondary); font-style: italic;">Chưa xem công việc nào.</p>';
        }
    }

    if (savedCoursesEl) {
        if (affiliateCourses && affiliateCourses.length > 0) {
            savedCoursesEl.innerHTML = affiliateCourses.slice(0, 2).map(c => {
                const logoFile = c.provider === 'BISC' ? 'bisc.jpg' :
                                 c.provider === 'Datapot' ? 'datapot.png' :
                                 c.provider === 'Tomorrow Marketers' ? 'tomorrow_marketers.jpg' :
                                 c.provider === 'UniTrain' ? 'unitrain.png' : '';
                return `
                    <div style="background: #fff; border: 1px solid #e9ecef; border-radius: 8px; padding: 12px; display:flex; align-items:center;">
                        ${logoFile ? `<img src="logos/${logoFile}" alt="${c.provider}" style="height:24px; width:auto; margin-right:8px;">` : ''}
                        <div style="flex-grow:1;">
                            <h4 style="font-size: 14px; margin:0 0 4px 0; color: #333;">${c.title}</h4>
                            <p style="font-size: 12px; color: #777; margin:0;">${c.provider}</p>
                            <a href="${c.url}" target="_blank" style="color: #007bff; font-size: 12px; text-decoration: none;">Xem lại khóa học &rarr;</a>
                        </div>
                    </div>`;
            }).join('');
        } else {
            savedCoursesEl.innerHTML = '<p style="color: var(--text-secondary); font-style: italic;">Chưa lưu khóa học nào.</p>';
        }
    }
}

// --- Profile & Skills Setup ---
function populateMajorDropdown() {
    const majors = [
        "Kinh tế đối ngoại", "Kinh tế quốc tế", "Kinh doanh quốc tế", "Quản trị kinh doanh",
        "Quản trị khách sạn", "Kế toán – Kiểm toán", "Luật", "Kinh tế chính trị",
        "Marketing", "Tài chính-Ngân hàng", "Ngôn ngữ Anh", "Ngôn ngữ Pháp", "Khoa học máy tính"
    ];
    
    const select = document.getElementById('profile-major');
    majors.forEach(m => {
        const option = document.createElement('option');
        option.value = m;
        option.textContent = m;
        select.appendChild(option);
    });

    select.addEventListener('change', (e) => {
        currentProfile.major = e.target.value;
        extractSkillsFromMajor(e.target.value);
    });
}

function extractSkillsFromMajor(major) {
    // Mocking matching logic based on major
    const majorSkillsMap = {
        "Kinh doanh quốc tế": ["Presentation", "Market Research", "Data Analysis", "Logistics", "Strategic Planning", "Negotiation", "Supply Chain", "English", "Communication"],
        "Khoa học máy tính": ["Python", "SQL", "C++", "Algorithm", "Database", "Machine Learning", "System Design", "Agile", "Scrum", "Git"],
        "Kinh tế đối ngoại": ["Communication", "English", "Negotiation", "Excel", "International Trade", "Import/Export", "Market Research", "Logistics"],
        "Quản trị kinh doanh": ["Management", "Leadership", "Excel", "Communication", "Agile", "Strategic Planning", "Operations", "Finance Basics", "Marketing Basics"],
        "Marketing": ["SEO", "Content Creation", "Communication", "Creativity", "Market Research", "Google Analytics", "Digital Marketing", "Copywriting", "Campaign Management"],
        "Tài chính-Ngân hàng": ["Excel", "Finance", "Analytical Skills", "PowerBI", "Risk Management", "Investment", "Accounting Basics", "SQL"]
    };
    
    // Default skills if not mapped
    const skills = majorSkillsMap[major] || ["Excel", "Communication", "Teamwork", "Problem Solving", "Presentation", "Time Management", "Critical Thinking"];
    
    // Add to profile
    skills.forEach(s => {
        const lowerS = s.toLowerCase();
        if(!currentProfile.skills.includes(lowerS)) currentProfile.skills.push(lowerS);
    });
    
    renderProfileForm();
}

// CV Upload Mock
document.getElementById('cv-upload').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('cv-tags').innerHTML = '<span class="empty-tag-msg">Đang phân tích CV...</span>';
        
        const reader = new FileReader();
        reader.onload = function(event) {
            const fileContent = event.target.result.toLowerCase();
            const fileNameLower = file.name.toLowerCase();
            
            setTimeout(() => {
                const detectedSkills = [];
                const masterSkills = [
                    'Data Analysis', 'SQL', 'Python', 'Financial Modeling', 
                    'Market Research', 'Logistics', 'Strategic Planning', 
                    'Content Marketing', 'Digital Marketing', 'Presentation', 'Problem Solving'
                ];
                
                masterSkills.forEach(skill => {
                    const skLower = skill.toLowerCase();
                    if (fileContent.includes(skLower) || fileNameLower.includes(skLower)) {
                        detectedSkills.push(skLower);
                    }
                });
                
                if (detectedSkills.length === 0) {
                    // Fallback to basic soft skills if none of the master skills are explicitly found
                    detectedSkills.push("communication", "excel", "problem solving");
                }
                
                detectedSkills.forEach(s => {
                    if(!currentProfile.skills.includes(s)) {
                        currentProfile.skills.push(s);
                    }
                });
                
                renderProfileForm();
            }, 1500);
        };
        reader.readAsText(file);
    }
});

function renderTags(containerId, skills, removable = false) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    
    if (skills.length === 0) {
        container.innerHTML = '<span class="empty-tag-msg">Không có kỹ năng</span>';
        return;
    }

    skills.forEach(skill => {
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.innerHTML = `${skill.toUpperCase()}`;
        if (removable) {
            const removeBtn = document.createElement('span');
            removeBtn.className = 'remove-tag';
            removeBtn.innerHTML = '&times;';
            removeBtn.onclick = () => {
                currentProfile.skills = currentProfile.skills.filter(s => s !== skill.toLowerCase());
                tag.remove();
            };
            tag.appendChild(removeBtn);
        }
        container.appendChild(tag);
    });
}

document.getElementById('save-profile-btn').addEventListener('click', () => {
    // Capture inputs
    currentProfile.name = document.getElementById('profile-name').value;
    currentProfile.dob = document.getElementById('profile-dob').value;
    currentProfile.major = document.getElementById('profile-major').value;

    // Save to localStorage
    localStorage.setItem('careerHubProfile', JSON.stringify(currentProfile));
    alert("Đã lưu hồ sơ thành công! Đang chuyển đến bảng tổng hợp.");
    
    switchToView('profile-dashboard-view');
});

// --- Jobs 2-Column Logic ---
function renderJobList() {
    const jobListEl = document.getElementById('job-list');
    jobListEl.innerHTML = '';
    
    const searchInput = document.getElementById('job-search');
    const categoryInput = document.getElementById('job-category');
    
    let filteredJobs = jobsData;
    
    if (searchInput && searchInput.value) {
        const q = searchInput.value.toLowerCase();
        filteredJobs = filteredJobs.filter(j => 
            (j.title && j.title.toLowerCase().includes(q)) || 
            (j.company && j.company.toLowerCase().includes(q))
        );
    }
    
    if (categoryInput && categoryInput.value) {
        filteredJobs = filteredJobs.filter(j => j.family === categoryInput.value);
    }

    const countEl = document.getElementById('job-count-text');
    if (countEl) countEl.textContent = `${filteredJobs.length} Jobs Found`;

    if (filteredJobs.length === 0) {
        jobListEl.innerHTML = '<div style="padding: 20px; text-align: center; color: #6c757d;">Không tìm thấy công việc phù hợp...</div>';
        return;
    }

    filteredJobs.forEach(job => {
        const card = document.createElement('div');
        card.className = 'job-card';
        
        let logoHTML = '';
        if (job.logo && job.logo.startsWith('http')) {
            logoHTML = `<img src="${job.logo}" alt="Logo" style="width: 48px; height: 48px; object-fit: contain; border-radius: 6px;">`;
        } else {
            logoHTML = `<img src="favicon.png" alt="Default Logo" style="width: 48px; height: 48px; object-fit: contain; border-radius: 6px;">`;
        }
        
        const isIntern = job.title && job.title.toLowerCase().includes('thực tập');

        card.innerHTML = `
            <div style="display: flex; gap: 16px;">
                ${logoHTML}
                <div style="flex-grow: 1; padding-right: 20px;">
                    <div class="job-card-bookmark"><i class="fa-regular fa-bookmark"></i></div>
                    <div class="job-card-title">${job.title}</div>
                    <div class="job-card-company">${job.company}</div>
                    <span class="job-card-tag">${isIntern ? 'INTERNSHIP' : 'FULL-TIME'}</span>
                    <div class="job-card-meta">
                        <span><i class="fa-regular fa-calendar" style="margin-right: 4px;"></i> 30-06-2026</span>
                        <span><i class="fa-solid fa-location-dot" style="margin-right: 4px;"></i> ${job.location || 'Hà Nội / HCM'}</span>
                        <div class="job-card-salary">${job.salary || 'Thỏa thuận'}</div>
                    </div>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            // Remove active class from all
            document.querySelectorAll('.job-card').forEach(c => c.classList.remove('active'));
            // Add active border to this
            card.classList.add('active');
            showJobDetails(job);
        });
        
        jobListEl.appendChild(card);
    });
}

// --- Insights Logic ---
function showInsights(industry) {
    document.getElementById('insight-title').textContent = `Insight: Ngành ${industry}`;
    
    // Default fallback
    let count = 0;
    let avgSal = "Đang cập nhật";
    let topSkills = [
        {name: "Tiếng Anh", countText: "80%", rawCount: 80},
        {name: "Tin học văn phòng", countText: "60%", rawCount: 60},
        {name: "Giao tiếp", countText: "50%", rawCount: 50}
    ];
    
    if (rawInsightsData) {
        // Find mapped industry (or use default)
        const familyMap = {
            "Marketing": "Marketing",
            "Finance": "Finance",
            "Data": "Data/Business Analysis",
            "HR": "HR",
            "Business Development": "Business Development"
        };
        
        const mappedFamily = familyMap[industry] || industry;
        
        const counts = rawInsightsData.Job_Counts_By_Family;
        if (counts && counts[mappedFamily]) {
            count = counts[mappedFamily];
        }
        
        if (rawInsightsData.Top_10_Skills) {
            const entries = Object.entries(rawInsightsData.Top_10_Skills).slice(0, 5);
            topSkills = entries.map(e => ({ name: e[0], countText: e[1] + " jobs", rawCount: e[1] }));
        }
    }
    
    document.getElementById('insight-job-count').textContent = count;
    document.getElementById('insight-avg-salary').textContent = avgSal;
    
    const skillsContainer = document.getElementById('insight-top-skills');
    skillsContainer.innerHTML = '';
    
    // Find max count to scale bars
    const maxCount = Math.max(...topSkills.map(s => s.rawCount), 1);
    
    skillsContainer.style.display = 'flex';
    skillsContainer.style.flexDirection = 'column';
    skillsContainer.style.gap = '12px';
    skillsContainer.style.width = '100%';

    topSkills.forEach(s => {
        const percent = Math.round((s.rawCount / maxCount) * 100);
        skillsContainer.innerHTML += `
            <div style="display: flex; align-items: center; width: 100%; gap: 12px;">
                <div style="width: 140px; font-size: 14px; font-weight: 500; color: #495057; text-transform: capitalize; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${s.name}">${s.name}</div>
                <div style="flex-grow: 1; background: #e9ecef; border-radius: 6px; height: 28px; overflow: hidden; position: relative;">
                    <div style="width: ${percent}%; height: 100%; background: linear-gradient(90deg, #007bff, #0056b3); border-radius: 6px; display: flex; align-items: center; padding-left: 12px; color: #fff; font-size: 13px; font-weight: bold; transition: width 0.5s ease-out;">
                        ${percent > 15 ? s.countText : ''}
                    </div>
                </div>
                ${percent <= 15 ? `<div style="font-size: 13px; font-weight: bold; color: #007bff;">${s.countText}</div>` : `<div style="width: 40px;"></div>`}
            </div>
        `;
    });
}

function formatJobDescription(descText) {
    if (!descText) return "<p class='jd-paragraph'>Chi tiết công việc sẽ được trao đổi khi phỏng vấn.</p>";
    
    const lines = descText.split(/\r?\n/);
    let html = '';
    
    const headerNames = [
        "Địa điểm làm việc", "Thời gian làm việc", "Mô tả công việc", 
        "Quyền lợi", "Yêu cầu tuyển dụng", "Yêu cầu công việc", 
        "Cách thức ứng tuyển", "Thông tin liên hệ", "Chế độ đãi ngộ", 
        "Quyền lợi được hưởng", "Yêu cầu", "Yêu cầu hồ sơ", "Mô tả chi tiết"
    ];
    
    let prevWasEmpty = false;
    lines.forEach(line => {
        let trimmed = line.trim();
        if (!trimmed) {
            if (!prevWasEmpty) {
                html += '<div class="jd-spacer"></div>';
                prevWasEmpty = true;
            }
            return;
        }
        prevWasEmpty = false;
        
        let isHeader = false;
        let headerTitle = "";
        let headerBody = "";
        
        for (let name of headerNames) {
            const pattern = new RegExp(`^(\\d+\\.\\s*)?(${name})(:?\\s*(.*))?$`, 'i');
            const match = trimmed.match(pattern);
            if (match) {
                isHeader = true;
                const numPrefix = match[1] || "";
                const headerName = match[2];
                headerTitle = numPrefix + headerName + ":";
                headerBody = match[4] || "";
                break;
            }
        }
        
        if (isHeader) {
            if (headerBody) {
                html += `<h3 class="jd-section-title">${headerTitle} <span class="jd-section-text">${headerBody}</span></h3>`;
            } else {
                html += `<h3 class="jd-section-title">${headerTitle}</h3>`;
            }
        } else {
            const bulletMatch = trimmed.match(/^([-\*•\+])\s*(.*)/);
            if (bulletMatch) {
                html += `<p class="jd-list-item">${bulletMatch[2]}</p>`;
            } else {
                const isSubHeader = trimmed.length < 50 && !trimmed.endsWith('.') && /^[A-ZÀ-Ỹ]/.test(trimmed);
                if (isSubHeader) {
                    html += `<p class="jd-sub-header">${trimmed}</p>`;
                } else {
                    html += `<p class="jd-paragraph">${trimmed}</p>`;
                }
            }
        }
    });
    
    return html;
}

let activeJob = null;
function showJobDetails(job) {
    const detailEl = document.getElementById('job-detail');
    if (!detailEl) return;
    
    // Formatting skills for display
    const reqSkills = job.required_skills && job.required_skills.length > 0 ? job.required_skills.join(', ') : 'Không yêu cầu cụ thể';
    
    const isIntern = job.title && job.title.toLowerCase().includes('thực tập');

    detailEl.innerHTML = `
        <div class="job-detail-banner">GROW TOGETHER</div>
        
        <div class="job-detail-header-card">
            <div class="jd-header-left">
                <img src="favicon.png" alt="Default Logo" style="width: 72px; height: 72px; object-fit: contain; border-radius: 6px;">
                <div class="jd-header-info">
                    <h2>${job.title}</h2>
                    <p style="font-weight: 500;">${job.company}</p>
                    <div class="jd-header-meta">
                        ${isIntern ? 'INTERNSHIP' : 'FULL-TIME'} | ${job.location || 'Hà Nội / HCM'} | <span class="salary">${job.salary || 'Thỏa thuận'}</span>
                    </div>
                </div>
            </div>
            <div class="jd-header-right">
                <button class="btn-apply" onclick="alert('Đã gửi hồ sơ ứng tuyển thành công!')">Apply Now</button>
            </div>
        </div>

        <div class="jd-tabs">
            <button class="tab-btn active" data-tab="tab-jd">Job Details</button>
            <button class="tab-btn" data-tab="tab-company">Company Overview</button>
            <button class="tab-btn" data-tab="tab-skill-match" id="run-match-btn-auto">Skill Match Analysis</button>
        </div>

        <div class="jd-tab-content">
            <!-- JD Tab -->
            <div id="tab-jd" class="jd-tab-pane active">
                <div class="jd-container-content">
                    <div class="jd-priority-skills">
                        <span class="jd-priority-skills-label">Kỹ năng ưu tiên:</span>
                        <span class="jd-priority-skills-value">${reqSkills}</span>
                    </div>
                    <div class="jd-body-parsed">
                        ${formatJobDescription(job.desc)}
                    </div>
                </div>
            </div>

            <!-- Company Tab -->
            <div id="tab-company" class="jd-tab-pane">
                <div style="color: #495057; line-height: 1.6;">
                    <p><strong>${job.company}</strong> là một trong những đơn vị tuyển dụng uy tín trong lĩnh vực <strong>${job.family}</strong>.</p>
                    <p>Chúng tôi mang đến môi trường làm việc chuyên nghiệp, thân thiện và cơ hội phát triển bản thân rộng mở. Tham gia cùng chúng tôi để kiến tạo những giá trị tốt đẹp!</p>
                </div>
            </div>

            <!-- Skill Match Tab -->
            <div id="tab-skill-match" class="jd-tab-pane">
                <div id="match-results" class="match-results">
                    <!-- Similar to old column 3 content -->
                    <div class="match-score">
                        <svg class="circular-chart" viewBox="0 0 36 36">
                            <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                            <path id="score-circle" class="circle" stroke-dasharray="0, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                            <text x="18" y="20.35" class="percentage" id="score-text">0%</text>
                        </svg>
                    </div>
                    <div class="match-skills">
                        <h4>Kỹ năng đã có <i class="fa-solid fa-circle-check" style="color: var(--green-success); margin-left: 4px;"></i></h4>
                        <div class="tags-container" id="matched-skills"></div>
                        <h4>Kỹ năng còn thiếu <i class="fa-solid fa-circle-xmark" style="color: var(--accent); margin-left: 4px;"></i></h4>
                        <div class="tags-container" id="missing-skills"></div>
                    </div>
                    <div class="course-recommendations">
                        <h4>Khóa học Bổ trợ (Affiliate)</h4>
                        <div class="course-list" id="affiliate-courses"></div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Tab Switching Logic
    const tabBtns = detailEl.querySelectorAll('.tab-btn');
    const tabPanes = detailEl.querySelectorAll('.jd-tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            detailEl.querySelector('#' + targetId).classList.add('active');
            
            if (targetId === 'tab-skill-match') {
                runMatchCalculation(job);
            }
        });
    });

    activeJob = job;
}

const skillAliases = {
    'Financial Modeling': ['finance', 'financial', 'accounting', 'acca', 'cfa', 'cma', 'financial modeling', 'audit'],
    'Data Analysis': ['data analysis', 'data analyst', 'analytics', 'dashboard', 'power bi', 'excel', 'data processing'],
    'SQL': ['sql', 'mysql', 'postgresql', 'query', 'database'],
    'Python': ['python', 'pandas', 'numpy', 'machine learning'],
    'Digital Marketing': ['marketing', 'digital marketing', 'seo', 'campaign', 'social media'],
    'Content Marketing': ['content', 'copywriting', 'content marketing', 'writing'],
    'Market Research': ['research', 'market research', 'competitor', 'insight'],
    'Strategic Planning': ['strategy', 'strategic', 'planning', 'sbl', 'management'],
    'Presentation': ['presentation', 'communication', 'present', 'public speaking', 'negotiation'],
    'Problem Solving': ['problem solving', 'problem-solving', 'analytical', 'solution'],
    'Logistics': ['logistics', 'supply chain', 'warehouse', 'freight', 'transportation', 'export', 'import']
};

function runMatchCalculation(job) {
    if (!job) return;
    
    // 1. Dynamic required skills extraction using regex & aliases from the job description
    const jdLower = ((job.desc || "") + " " + (job.title || "")).toLowerCase();
    const required = [];
    
    Object.entries(skillAliases).forEach(([skillName, aliases]) => {
        const matchFound = [skillName, ...aliases].some(term => {
            const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const pattern = new RegExp('\\b' + escapedTerm + '\\b', 'i');
            return pattern.test(jdLower);
        });
        
        if (matchFound) {
            required.push(skillName);
        }
    });
    
    // Fallback to pre-loaded job.required_skills if text scanning yielded nothing
    if (required.length === 0 && job.required_skills && job.required_skills.length > 0) {
        required.push(...job.required_skills);
    }
    
    // Filter out soft skills to count domain knowledge & tools only
    const ignoreSkills = ['tiếng anh', 'giao tiếp', 'english', 'communication', 'teamwork', 'tin học văn phòng', 'problem solving', 'time management', 'thuyết trình', 'presentation'];
    const filteredRequired = required.filter(s => !ignoreSkills.includes(s.toLowerCase()));
    
    // Normalize user skills to lowercase
    const userSkills = (currentProfile.skills || []).map(s => s.toLowerCase());
    
    // 2. Perform case-insensitive, alias-aware match
    const matched = [];
    const missing = [];
    
    filteredRequired.forEach(reqSkill => {
        const reqSkillLower = reqSkill.toLowerCase();
        let isMatched = userSkills.includes(reqSkillLower);
        
        if (!isMatched && skillAliases[reqSkill]) {
            isMatched = skillAliases[reqSkill].some(alias => userSkills.includes(alias.toLowerCase()));
        }
        
        if (isMatched) {
            matched.push(reqSkill);
        } else {
            missing.push(reqSkill);
        }
    });

    // 3. Domain Knowledge Evaluation
    const jobFamily = job.family;
    const familyDomainMap = {
        "Finance": ["finance", "financial modeling", "tài chính", "cfa", "acca", "accounting", "kiểm toán", "kế toán"],
        "Marketing": ["marketing", "digital marketing", "tiếp thị", "branding", "seo"],
        "Data/Business Analysis": ["data analysis", "dữ liệu", "analytics", "sql", "python", "powerbi"],
        "HR": ["hr", "human resources", "nhân sự", "tuyển dụng"],
        "Business Development": ["business development", "kinh doanh", "sales", "bán hàng", "negotiation", "đàm phán"],
        "Logistics": ["logistics", "supply chain", "chuỗi cung ứng", "xuất nhập khẩu", "import", "export"]
    };

    const majorDomainMap = {
        "Kinh doanh quốc tế": ["Business Development", "Logistics"],
        "Quản trị kinh doanh": ["Business Development", "HR"],
        "Marketing": ["Marketing"],
        "Tài chính-Ngân hàng": ["Finance"],
        "Kế toán – Kiểm toán": ["Finance"],
        "Khoa học máy tính": ["Data/Business Analysis"],
        "Kinh tế đối ngoại": ["Business Development", "Logistics", "Finance"]
    };

    let totalRequiredLength = filteredRequired.length;
    if (jobFamily && familyDomainMap[jobFamily]) {
        totalRequiredLength += 1;
        
        const domainDisplayName = jobFamily === "Finance" ? "Finance / Tài chính" :
                                  jobFamily === "Marketing" ? "Marketing / Tiếp thị" :
                                  jobFamily === "Data/Business Analysis" ? "Data Analysis / Phân tích dữ liệu" :
                                  jobFamily === "HR" ? "Human Resources / Nhân sự" :
                                  jobFamily === "Business Development" ? "Business Development / Kinh doanh" :
                                  jobFamily === "Logistics" ? "Logistics / Chuỗi cung ứng" : jobFamily;

        // Check if user has domain knowledge either from profile skills OR from their major
        const hasDomainSkill = familyDomainMap[jobFamily].some(s => userSkills.includes(s));
        
        const userMajor = currentProfile.major;
        const majorMatchesDomain = userMajor && majorDomainMap[userMajor] && majorDomainMap[userMajor].includes(jobFamily);
        
        const userHasDomain = hasDomainSkill || majorMatchesDomain;
        
        if (userHasDomain) {
            matched.push(domainDisplayName);
        } else {
            missing.push(domainDisplayName);
        }
    }
    
    // Calculate percentage score
    const percentage = totalRequiredLength > 0 ? Math.round((matched.length / totalRequiredLength) * 100) : 100;
    
    // Update Score UI
    const circle = document.getElementById('score-circle');
    if (circle) {
        document.getElementById('score-text').textContent = `${percentage}%`;
        circle.setAttribute('stroke-dasharray', `${percentage}, 100`);
        circle.classList.remove('score-high', 'score-med', 'score-low');
        if (percentage >= 70) circle.classList.add('score-high');
        else if (percentage >= 40) circle.classList.add('score-med');
        else circle.classList.add('score-low');
    }
    
    // Render Skills Containers
    const matchedContainer = document.getElementById('matched-skills');
    if (matchedContainer) {
        matchedContainer.innerHTML = '';
        matched.forEach(s => {
            const span = document.createElement('span'); 
            span.className = 'tag success'; 
            span.textContent = s.toUpperCase();
            matchedContainer.appendChild(span);
        });
        if(matched.length === 0) matchedContainer.innerHTML = '<p style="color:#6c757d; font-size: 13px;">Chưa khớp kỹ năng nào.</p>';
    }
    
    const missingContainer = document.getElementById('missing-skills');
    if (missingContainer) {
        missingContainer.innerHTML = '';
        missing.forEach(s => {
            const span = document.createElement('span'); 
            span.className = 'tag danger'; 
            span.textContent = s.toUpperCase();
            missingContainer.appendChild(span);
        });
        if(missing.length === 0) missingContainer.innerHTML = '<p style="color:#6c757d; font-size: 13px;">Không thiếu kỹ năng nào!</p>';
    }
    
    // Render Course recommendations
    renderAffiliateCourses(missing);
}

function renderAffiliateCourses(missingSkills) {
    const container = document.getElementById('affiliate-courses');
    if (!container) return;
    container.innerHTML = '';
    
    if (missingSkills.length === 0) {
        container.innerHTML = '<p style="color:#28a745; font-size: 14px; font-weight: 500;">Bạn đã đáp ứng đủ các kỹ năng cốt lõi cho công việc này!</p>';
        return;
    }
    
    // Normalize missing skills to lowercase
    const normalizedMissing = missingSkills.map(s => s.toLowerCase());
    
    // 1. Find FTU internal courses
    const suggestedFtu = [];
    ftuCourses.forEach(course => {
        let matchScore = 0;
        
        normalizedMissing.forEach(skill => {
            const inDomain = course.domain_knowledge && course.domain_knowledge.some(s => s.includes(skill) || skill.includes(s));
            const inJd = course.jd_skills && course.jd_skills.some(s => s.includes(skill) || skill.includes(s));
            const inTools = course.tools && course.tools.some(s => s.includes(skill) || skill.includes(s));
            
            if (inDomain || inJd || inTools) {
                matchScore += 3;
            }
            
            // Special mappings for general domains
            if (skill.includes('finance') || skill.includes('tài chính')) {
                if (course.name.toLowerCase().includes('finance') || course.name.toLowerCase().includes('tài chính') || course.name.toLowerCase().includes('fin')) {
                    matchScore += 2;
                }
            }
            if (skill.includes('marketing') || skill.includes('tiếp thị')) {
                if (course.name.toLowerCase().includes('marketing') || course.name.toLowerCase().includes('tiếp thị') || course.name.toLowerCase().includes('mkt')) {
                    matchScore += 2;
                }
            }
            if (skill.includes('logistics') || skill.includes('chuỗi cung ứng')) {
                if (course.name.toLowerCase().includes('logistics') || course.name.toLowerCase().includes('vận tải') || course.name.toLowerCase().includes('chuỗi cung ứng')) {
                    matchScore += 2;
                }
            }
        });
        
        if (matchScore > 0) {
            suggestedFtu.push({ ...course, score: matchScore });
        }
    });
    
    const topFtu = suggestedFtu.sort((a, b) => b.score - a.score).slice(0, 3);
    
    // 2. Find external courses
    const suggestedExt = [];
    externalCourses.forEach(course => {
        let matchScore = 0;
        const catLower = (course.category || "").toLowerCase();
        const titleLower = (course.title || "").toLowerCase();
        
        normalizedMissing.forEach(skill => {
            if (catLower.includes(skill) || titleLower.includes(skill)) {
                matchScore += 5;
            }
            
            if (skillAliases[skill]) {
                skillAliases[skill].forEach(alias => {
                    const alLower = alias.toLowerCase();
                    if (catLower.includes(alLower) || titleLower.includes(alLower)) {
                        matchScore += 3;
                    }
                });
            }
            
            if (skill.includes('finance') || skill.includes('tài chính') || skill.includes('financial')) {
                if (catLower.includes('financial') || titleLower.includes('cfa') || titleLower.includes('acca')) {
                    matchScore += 4;
                }
            }
            
            if (skill.includes('marketing') || skill.includes('tiếp thị')) {
                if (catLower.includes('marketing') || titleLower.includes('marketing')) {
                    matchScore += 4;
                }
            }
            
            if (skill.includes('data analysis') || skill.includes('phân tích dữ liệu') || skill.includes('dữ liệu')) {
                if (catLower.includes('data') || catLower.includes('python') || catLower.includes('sql') || titleLower.includes('data') || titleLower.includes('power bi')) {
                    matchScore += 4;
                }
            }
        });
        
        if (matchScore > 0) {
            suggestedExt.push({ ...course, score: matchScore });
        }
    });
    
    const topExt = suggestedExt.sort((a, b) => b.score - a.score).slice(0, 3);
    
    // 3. Render layouts
    let htmlContent = '<div style="display: flex; flex-direction: column; gap: 20px; margin-top: 10px;">';
    
    if (topFtu.length > 0) {
        htmlContent += `
            <div>
                <h5 style="color: #2b3149; font-size: 14px; font-weight: 600; margin-bottom: 8px; border-bottom: 2px solid #e91e63; padding-bottom: 4px; display: inline-block;">
                    🏫 Môn học nội bộ (ĐH Ngoại Thương)
                </h5>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    ${topFtu.map(c => `
                        <div class="course-item" style="background: #fff; padding: 10px; border-radius: 6px; border-left: 3px solid #e91e63; border-top: 1px solid #eee; border-right: 1px solid #eee; border-bottom: 1px solid #eee;">
                            <div style="font-size: 11px; font-weight: bold; color: #666; margin-bottom: 2px;">Mã học phần: ${c.code}</div>
                            <h5 style="margin: 0 0 4px 0; font-size: 14px; color: #2b3149; font-weight: 600;">${c.name}</h5>
                            <p style="margin: 0; font-size: 12px; color: #555; font-style: italic;">Phù hợp để bổ sung kỹ năng chuyên sâu</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    if (topExt.length > 0) {
        htmlContent += `
            <div>
                <h5 style="color: #2b3149; font-size: 14px; font-weight: 600; margin-bottom: 8px; border-bottom: 2px solid #2b3149; padding-bottom: 4px; display: inline-block;">
                    🌐 Khóa học thực chiến (Trung tâm ngoài)
                </h5>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    ${topExt.map(c => `
                        <div class="course-item" style="background: #fff; padding: 10px; border-radius: 6px; border-left: 3px solid #2b3149; border-top: 1px solid #eee; border-right: 1px solid #eee; border-bottom: 1px solid #eee;">
                            <h5 style="margin: 0 0 2px 0; font-size: 14px; color: #2b3149; font-weight: 600;">${c.title}</h5>
                            <p style="margin: 0 0 6px 0; font-size: 12px; color: #666;">Trung tâm: <b>${c.provider}</b></p>
                            <a href="${c.url}" target="_blank" class="btn-sm" style="display: inline-block; background: #2b3149; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; text-decoration: none; font-weight: 500;">Tìm hiểu thêm 🔗</a>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    if (topFtu.length === 0 && topExt.length === 0) {
        htmlContent += '<p style="font-size:12px; color:#6c757d; font-style:italic;">Chưa có lộ trình cụ thể cho các kỹ năng này.</p>';
    }
    
    htmlContent += '</div>';
    container.innerHTML = htmlContent;
}
