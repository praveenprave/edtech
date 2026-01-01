"use client";
import React, { useState } from 'react';
import { BookOpen, Video, PlayCircle, CheckCircle2, ChevronRight, ChevronDown, Wand2, Settings, User, Menu, X } from 'lucide-react';

// Mock Data from "Document AI"
const BOOK_STRUCTURE = {
  title: "Physics - Grade 12 (Volume 1)",
  units: [
    {
      id: "U1", title: "Electrostatics", topics: [
        { id: "PHY12_01_01", title: "Introduction to Electrostatics", cached: true },
        { id: "PHY12_01_02", title: "Coulomb's Law", cached: true },
        { id: "PHY12_01_03", title: "Electric Field Lines", cached: false },
        { id: "PHY12_01_04", title: "Electric Dipole", cached: false },
      ]
    },
    {
      id: "U2", title: "Current Electricity", topics: [
        { id: "PHY12_02_01", title: "Electric Current", cached: true },
        { id: "PHY12_02_02", title: "Ohm's Law", cached: true },
      ]
    }
  ]
};

export default function TeacherDashboard() {
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [expandedUnits, setExpandedUnits] = useState<string[]>(['U1']);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Customization State
  const [teacherName, setTeacherName] = useState("Mrs. Sarah");
  const [tone, setTone] = useState("Concept Focused");
  const [lang, setLang] = useState("English");

  const toggleUnit = (unitId: string) => {
    setExpandedUnits(prev => prev.includes(unitId) ? prev.filter(id => id !== unitId) : [...prev, unitId]);
  }

  const handleGenerate = () => {
    if (!selectedTopic) return;
    setIsGenerating(true);
    // Simulate API call
    setTimeout(() => {
      setIsGenerating(false);
      alert(`Lesson Generation Started for topic: ${selectedTopic}\nWith Auto-Stitched Intro for: ${teacherName}`);
    }, 2000);
  }

  // --- File Upload Logic ---
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      // 1. Get Signed URL
      // Note: In prod, replace localhost with env var or relative path if proxied
      // We use relative path assuming Next.js rewrites or same domain
      // BUT for this demo we assume backend is at :8000. 
      // Correct approach: Use a defined API_BASE_URL.
      const API_BASE_URL = "https://rag-backend-856401490977.us-central1.run.app"; // Fallback to potential cloud run url or use relative
      // Actually, let's try relative '/api/v1' if we have a proxy, else assume direct core url
      // For now, I'll alert the user if it fails.

      const res = await fetch(`/api/v1/upload-url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: file.name, content_type: file.type })
      });

      if (!res.ok) throw new Error("Failed to get upload URL");

      const { upload_url, gcs_uri } = await res.json();

      // 2. Upload to GCS
      const uploadRes = await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': file.type }
      });

      if (!uploadRes.ok) throw new Error("Failed to upload to GCS");

      alert(`✅ Upload Complete!\nFile: ${file.name}\nURI: ${gcs_uri}\n\nThe Brain is now processing it. Integration pending.`);

    } catch (err) {
      console.error(err);
      alert("❌ Upload Failed: " + err);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden">

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar: Customization Panel */}
      {/* Responsive Logic: Fixed Sidebar on Desktop, Drawer on Mobile */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-80 bg-white border-r border-slate-200 flex flex-col transition-transform duration-300 transform 
        md:relative md:translate-x-0 
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="p-6 border-b border-slate-100 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="bg-brand-600 text-white p-2 rounded-lg">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-slate-900">EduGen AI</h1>
              <p className="text-xs text-slate-500">Teacher Workspace</p>
            </div>
          </div>
          <button onClick={() => setIsMobileMenuOpen(false)} className="md:hidden text-slate-500">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Upload Action */}
        <div className="px-6 pt-4 pb-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept=".pdf"
          />
          <button
            onClick={handleUploadClick}
            disabled={isUploading}
            className="w-full flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white py-2.5 rounded-lg text-sm font-medium transition"
          >
            {isUploading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <BookOpen className="w-4 h-4" />
                Upload Textbook
              </>
            )}
          </button>
        </div>

        <div className="p-6 space-y-8 flex-1 overflow-y-auto">
          {/* Teacher Profile */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <User className="w-3 h-3" /> Personalization
            </h3>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Teacher Name</label>
              <input
                type="text"
                value={teacherName}
                onChange={(e) => setTeacherName(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-brand-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Avatar Identity</label>
              <select className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
                <option>Generic Female (Sarah)</option>
                <option>Generic Male (Mike)</option>
                <option>Custom Clone (My Face)</option>
              </select>
            </div>
          </div>

          {/* Lesson Config */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Settings className="w-3 h-3" /> Lesson Config
            </h3>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Language</label>
              <div className="flex gap-2 flex-wrap">
                {['English', 'Tamil', 'Hindi'].map(l => (
                  <button
                    key={l}
                    onClick={() => setLang(l)}
                    className={`px-3 py-1.5 text-xs rounded-full border transition ${lang === l ? 'bg-brand-50 border-brand-500 text-brand-700 font-medium' : 'border-slate-200 text-slate-600 hover:bg-slate-50'}`}
                  >
                    {l}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Tone</label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white"
              >
                <option>Concept Focused (Conceptual)</option>
                <option>Exam Oriented (Fast Paced)</option>
                <option>Story Driven (Engaging)</option>
              </select>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center font-bold text-xs">
              S
            </div>
            <div className="text-sm">
              <div className="font-medium">Sarah Jenkins</div>
              <div className="text-xs text-slate-500">Grade 12 Physics</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content: Topic Tree */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative w-full">
        {/* Header */}
        <header className="h-16 border-b border-slate-200 flex items-center justify-between px-4 md:px-8 bg-white shrink-0">
          <div className="flex items-center gap-4">
            {/* Mobile Hamburger */}
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="md:hidden p-2 -ml-2 text-slate-600 hover:bg-slate-100 rounded-lg"
            >
              <Menu className="w-6 h-6" />
            </button>

            <div className="hidden md:flex items-center gap-4">
              <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-medium border border-green-200 whitespace-nowrap">
                Document AI Parsed
              </span>
              <h2 className="text-lg font-semibold text-slate-800 truncate max-w-[200px] lg:max-w-none">{BOOK_STRUCTURE.title}</h2>
            </div>

            {/* Mobile Title Replacement */}
            <h2 className="md:hidden text-sm font-semibold text-slate-800 truncate">{BOOK_STRUCTURE.title}</h2>
          </div>

          <div className="text-xs md:text-sm text-slate-500 hidden sm:block">
            Synced: 10:00 AM
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 bg-slate-50/50 w-full">
          <div className="max-w-4xl mx-auto">
            <div className="mb-6">
              <h1 className="text-xl md:text-2xl font-bold text-slate-900">Select a Topic</h1>
              <p className="text-sm md:text-base text-slate-600 mt-1">Select a topic to generate a custom stitched lesson.</p>
            </div>

            <div className="space-y-4 pb-24 md:pb-0">
              {BOOK_STRUCTURE.units.map((unit) => (
                <div key={unit.id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                  {/* Unit Header */}
                  <div
                    onClick={() => toggleUnit(unit.id)}
                    className="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-50 transition"
                  >
                    <div className="flex items-center gap-3 overflow-hidden">
                      {expandedUnits.includes(unit.id) ? <ChevronDown className="w-5 h-5 text-slate-400 shrink-0" /> : <ChevronRight className="w-5 h-5 text-slate-400 shrink-0" />}
                      <span className="font-semibold text-slate-700 truncate">{unit.title}</span>
                      <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full shrink-0">
                        {unit.topics.length}
                      </span>
                    </div>
                  </div>

                  {/* Topics List */}
                  {expandedUnits.includes(unit.id) && (
                    <div className="border-t border-slate-100">
                      {unit.topics.map((topic) => (
                        <div
                          key={topic.id}
                          onClick={() => setSelectedTopic(topic.id)}
                          className={`p-4 flex items-center justify-between border-b border-slate-50 last:border-0 cursor-pointer transition ${selectedTopic === topic.id ? 'bg-brand-50/50' : 'hover:bg-slate-50'}`}
                        >
                          <div className="flex items-center gap-3 overflow-hidden">
                            <div className={`w-5 h-5 shrink-0 rounded-full border flex items-center justify-center transition ${selectedTopic === topic.id ? 'border-brand-600 bg-brand-600' : 'border-slate-300'}`}>
                              {selectedTopic === topic.id && <div className="w-2 h-2 bg-white rounded-full" />}
                            </div>
                            <div className="min-w-0">
                              <div className={`font-medium truncate ${selectedTopic === topic.id ? 'text-brand-900' : 'text-slate-700'}`}>
                                {topic.title}
                              </div>
                              <div className="flex items-center gap-2 mt-1 flex-wrap">
                                {topic.cached ? (
                                  <span className="text-[10px] text-green-600 flex items-center gap-1 bg-green-50 px-1.5 rounded shrink-0">
                                    <CheckCircle2 className="w-3 h-3" /> Ready
                                  </span>
                                ) : (
                                  <span className="text-[10px] text-amber-600 flex items-center gap-1 bg-amber-50 px-1.5 rounded shrink-0">
                                    <Wand2 className="w-3 h-3" /> Generate
                                  </span>
                                )}
                                <span className="text-[10px] text-slate-400 hidden sm:inline">ID: {topic.id}</span>
                              </div>
                            </div>
                          </div>
                          {/* Preview/Action */}
                          {selectedTopic === topic.id && (
                            <div className="flex gap-2 shrink-0 ml-2">
                              <button className="bg-white border border-slate-200 p-2 rounded-lg text-slate-500 hover:text-brand-600 hover:border-brand-200 transition">
                                <PlayCircle className="w-5 h-5" />
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Action Bar */}
        <div className="h-auto md:h-20 bg-white border-t border-slate-200 px-4 py-4 md:px-8 flex flex-col md:flex-row items-center justify-between gap-4 shrink-0">
          <div className="text-sm w-full md:w-auto text-center md:text-left">
            {selectedTopic ? (
              <span className="text-slate-600">Selected: <span className="font-bold text-slate-900 block md:inline">{selectedTopic}</span></span>
            ) : (
              <span className="text-slate-400">Select a topic to proceed</span>
            )}
          </div>
          <button
            onClick={handleGenerate}
            disabled={!selectedTopic || isGenerating}
            className={`w-full md:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-white transition shadow-lg ${!selectedTopic || isGenerating ? 'bg-slate-300 cursor-not-allowed' : 'bg-brand-600 hover:bg-brand-700 shadow-brand-500/20'}`}
          >
            {isGenerating ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Wand2 className="w-5 h-5" />
                Create Lesson
              </>
            )}
          </button>
        </div>
      </main>
    </div>
  );
}

