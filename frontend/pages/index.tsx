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
        <title>Necessitas.ai - Intelligent Career Guidance</title>
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
                <span className="ml-2 text-2xl font-bold text-gray-900">Necessitas.ai</span>
              </div>
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
                className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto"
              >
                Get personalized career guidance, job recommendations, and skill development
                roadmaps powered by advanced AI technology.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="flex justify-center"
              >
                <Link
                  href="/chat"
                  className="inline-flex items-center px-12 py-6 bg-indigo-600 text-white font-bold text-lg rounded-xl hover:bg-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  <Target className="w-6 h-6 mr-3" />
                  Start Your Career Journey
                  <ArrowRight className="w-6 h-6 ml-3" />
                </Link>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Stats Section - Commented out for now */}
        {/* <section className="py-16 bg-white">
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
        </section> */}

        {/* How It Works Section */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-4xl font-bold text-gray-900 mb-4"
              >
                How Necessitas.ai Works
              </motion.h2>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="text-xl text-gray-600 max-w-3xl mx-auto"
              >
                Our AI-powered platform provides comprehensive career guidance through intelligent analysis and personalized recommendations
              </motion.p>
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


        {/* Footer */}
        <footer className="bg-gray-900 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="flex items-center justify-center mb-4">
                <Briefcase className="w-8 h-8 text-indigo-400" />
                <span className="ml-2 text-2xl font-bold">necessitas.ai</span>
              </div>
              <p className="text-gray-400 mb-4">
                Powered by AWS Bedrock AgentCore • Built for AWS AI Agent Global Hackathon 2025
              </p>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
