import { useState, useEffect } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  Target,
  Briefcase,
  Users,
  MapPin,
  DollarSign,
  Clock,
  Star,
  ArrowRight,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

export default function Dashboard() {
  const [userProfile, setUserProfile] = useState<any>(null);
  const [jobRecommendations, setJobRecommendations] = useState<any[]>([]);
  const [skillGap, setSkillGap] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading user data
    const loadDashboardData = async () => {
      try {
        // Mock data - in real app, fetch from API
        setUserProfile({
          name: "John Doe",
          title: "Software Engineer",
          location: "San Francisco, CA",
          experience: "3 years",
          skills: ["Python", "React", "AWS", "Machine Learning", "Docker"],
          targetRole: "Senior Software Engineer",
          salaryRange: "$120,000 - $150,000"
        });

        setJobRecommendations([
          {
            id: 1,
            title: "Senior Software Engineer",
            company: "TechCorp",
            location: "San Francisco, CA",
            salary: "$130,000 - $160,000",
            match: 95,
            skills: ["Python", "React", "AWS", "Machine Learning"],
            posted: "2 days ago",
            type: "Full-time"
          },
          {
            id: 2,
            title: "Full Stack Developer",
            company: "StartupXYZ",
            location: "Remote",
            salary: "$110,000 - $140,000",
            match: 88,
            skills: ["Python", "React", "Docker", "PostgreSQL"],
            posted: "1 week ago",
            type: "Full-time"
          },
          {
            id: 3,
            title: "Machine Learning Engineer",
            company: "AI Solutions Inc",
            location: "New York, NY",
            salary: "$140,000 - $180,000",
            match: 82,
            skills: ["Python", "Machine Learning", "TensorFlow", "AWS"],
            posted: "3 days ago",
            type: "Full-time"
          }
        ]);

        setSkillGap({
          missing: ["Kubernetes", "GraphQL", "Microservices"],
          developing: ["Leadership", "System Design", "DevOps"],
          strong: ["Python", "React", "AWS", "Machine Learning"]
        });

      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const salaryData = [
    { month: 'Jan', current: 95000, target: 120000 },
    { month: 'Feb', current: 98000, target: 125000 },
    { month: 'Mar', current: 102000, target: 130000 },
    { month: 'Apr', current: 105000, target: 135000 },
    { month: 'May', current: 108000, target: 140000 },
    { month: 'Jun', current: 112000, target: 145000 }
  ];

  const skillData = [
    { skill: 'Python', level: 90, demand: 95 },
    { skill: 'React', level: 85, demand: 88 },
    { skill: 'AWS', level: 80, demand: 92 },
    { skill: 'Machine Learning', level: 75, demand: 90 },
    { skill: 'Docker', level: 70, demand: 85 }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Dashboard - necessitas.ai</title>
        <meta name="description" content="Your personalized career dashboard" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Welcome back, {userProfile?.name}!</h1>
                <p className="text-gray-600">{userProfile?.title} • {userProfile?.location}</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm text-gray-500">Target Role</p>
                  <p className="font-semibold text-gray-900">{userProfile?.targetRole}</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Stats Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          >
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="flex items-center">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Briefcase className="w-6 h-6 text-indigo-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">Job Matches</p>
                  <p className="text-2xl font-bold text-gray-900">{jobRecommendations.length}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Target className="w-6 h-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">Match Score</p>
                  <p className="text-2xl font-bold text-gray-900">92%</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">Salary Growth</p>
                  <p className="text-2xl font-bold text-gray-900">+18%</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">Network</p>
                  <p className="text-2xl font-bold text-gray-900">247</p>
                </div>
              </div>
            </div>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Job Recommendations */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="lg:col-span-2"
            >
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">Job Recommendations</h2>
                  <button className="text-indigo-600 hover:text-indigo-700 font-medium">
                    View All
                  </button>
                </div>

                <div className="space-y-4">
                  {jobRecommendations.map((job, index) => (
                    <motion.div
                      key={job.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                          <p className="text-gray-600">{job.company}</p>
                          <div className="flex items-center mt-2 space-x-4 text-sm text-gray-500">
                            <div className="flex items-center">
                              <MapPin className="w-4 h-4 mr-1" />
                              {job.location}
                            </div>
                            <div className="flex items-center">
                              <DollarSign className="w-4 h-4 mr-1" />
                              {job.salary}
                            </div>
                            <div className="flex items-center">
                              <Clock className="w-4 h-4 mr-1" />
                              {job.posted}
                            </div>
                          </div>
                          <div className="flex flex-wrap gap-2 mt-3">
                            {job.skills.map((skill: string, skillIndex: number) => (
                              <span
                                key={skillIndex}
                                className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="ml-4 text-right">
                          <div className="flex items-center mb-2">
                            <Star className="w-4 h-4 text-yellow-500 mr-1" />
                            <span className="font-semibold text-gray-900">{job.match}%</span>
                          </div>
                          <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm">
                            Apply
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Skill Gap Analysis */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="space-y-6"
            >
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Skill Gap Analysis</h3>

                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Missing Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {skillGap?.missing?.map((skill: string, index: number) => (
                        <span key={index} className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Developing Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {skillGap?.developing?.map((skill: string, index: number) => (
                        <span key={index} className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Strong Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {skillGap?.strong?.map((skill: string, index: number) => (
                        <span key={index} className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Career Progress */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Career Progress</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Resume Optimization</span>
                    <span className="text-sm font-medium text-gray-900">85%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '85%' }}></div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Skill Development</span>
                    <span className="text-sm font-medium text-gray-900">72%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '72%' }}></div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Network Building</span>
                    <span className="text-sm font-medium text-gray-900">68%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '68%' }}></div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Salary Projection Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-8 bg-white rounded-xl shadow-sm p-6"
          >
            <h3 className="text-lg font-bold text-gray-900 mb-6">Salary Projection</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={salaryData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="current" stroke="#4F46E5" strokeWidth={2} />
                  <Line type="monotone" dataKey="target" stroke="#10B981" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </div>
      </main>
    </>
  );
}
