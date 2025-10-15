import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  Upload,
  Search,
  TrendingUp,
  Users,
  Briefcase,
  Target,
  ArrowRight,
  CheckCircle
} from 'lucide-react';

export default function Home() {
  const [isUploading, setIsUploading] = useState(false);

  const features = [
    {
      icon: <Upload className="w-8 h-8" />,
      title: "Resume Analysis",
      description: "Upload your resume and get instant AI-powered analysis of your skills and experience."
    },
    {
      icon: <Search className="w-8 h-8" />,
      title: "Job Matching",
      description: "Find personalized job recommendations based on your profile and career goals."
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: "Career Roadmap",
      description: "Get a step-by-step roadmap to achieve your career objectives."
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Market Insights",
      description: "Access real-time market trends and salary insights for your field."
    }
  ];

  const stats = [
    { label: "Jobs Analyzed", value: "10M+" },
    { label: "Users Helped", value: "50K+" },
    { label: "Success Rate", value: "85%" },
    { label: "Companies", value: "5K+" }
  ];

  return (
    <>
      <Head>
        <title>CareerCompassAI - Intelligent Career Guidance</title>
        <meta name="description" content="AI-powered career guidance and job matching platform" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <Briefcase className="w-8 h-8 text-indigo-600" />
                <span className="ml-2 text-2xl font-bold text-gray-900">CareerCompassAI</span>
              </div>
              <nav className="hidden md:flex space-x-8">
                <Link href="/dashboard" className="text-gray-600 hover:text-indigo-600">Dashboard</Link>
                <Link href="/upload" className="text-gray-600 hover:text-indigo-600">Upload Resume</Link>
                <Link href="/jobs" className="text-gray-600 hover:text-indigo-600">Find Jobs</Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-5xl md:text-6xl font-bold text-gray-900 mb-6"
              >
                Your AI Career
                <span className="text-indigo-600"> Compass</span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto"
              >
                Get personalized career guidance, job recommendations, and skill development
                roadmaps powered by advanced AI technology.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="flex flex-col sm:flex-row gap-4 justify-center"
              >
                <Link
                  href="/upload"
                  className="inline-flex items-center px-8 py-4 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Upload className="w-5 h-5 mr-2" />
                  Upload Resume
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
                <Link
                  href="/jobs"
                  className="inline-flex items-center px-8 py-4 bg-white text-indigo-600 font-semibold rounded-lg border-2 border-indigo-600 hover:bg-indigo-50 transition-colors"
                >
                  <Search className="w-5 h-5 mr-2" />
                  Browse Jobs
                </Link>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="text-center"
                >
                  <div className="text-3xl font-bold text-indigo-600 mb-2">{stat.value}</div>
                  <div className="text-gray-600">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                How CareerCompassAI Works
              </h2>
              <p className="text-xl text-gray-600">
                Our AI-powered platform provides comprehensive career guidance
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
                >
                  <div className="text-indigo-600 mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-indigo-600">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-4xl font-bold text-white mb-4">
                Ready to Advance Your Career?
              </h2>
              <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
                Join thousands of professionals who have found their dream jobs with CareerCompassAI
              </p>
              <Link
                href="/upload"
                className="inline-flex items-center px-8 py-4 bg-white text-indigo-600 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Target className="w-5 h-5 mr-2" />
                Get Started Now
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
            </motion.div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="flex items-center justify-center mb-4">
                <Briefcase className="w-8 h-8 text-indigo-400" />
                <span className="ml-2 text-2xl font-bold">CareerCompassAI</span>
              </div>
              <p className="text-gray-400 mb-4">
                Powered by AWS Bedrock AgentCore • Built for AWS AI Agent Global Hackathon 2025
              </p>
              <div className="flex justify-center space-x-6">
                <Link href="/dashboard" className="text-gray-400 hover:text-white">Dashboard</Link>
                <Link href="/upload" className="text-gray-400 hover:text-white">Upload</Link>
                <Link href="/jobs" className="text-gray-400 hover:text-white">Jobs</Link>
                <Link href="/insights" className="text-gray-400 hover:text-white">Insights</Link>
              </div>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
