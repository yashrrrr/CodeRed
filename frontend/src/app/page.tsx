'use client'

import { useState } from 'react'
import { Search, ChevronDown, Menu, X } from 'lucide-react'

export default function UpGradHome() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isDomainsOpen, setIsDomainsOpen] = useState(false)

  const domains = [
    'Data Science',
    'Machine Learning & AI',
    'MBA',
    'Marketing',
    'Management',
    'Technology'
  ]

  const courses = [
    {
      title: 'Executive Doctor of Business Administration from SSBM',
      university: 'Swiss School of Business and Management',
      type: 'DBA',
      logo: 'https://d2o2utebsixu4k.cloudfront.net/upgrad/uni-cards-logos/DBA+/Logos/Logo%2056x56_SSBM.svg'
    },
    {
      title: 'Doctor of Business Administration From Golden Gate University',
      university: 'Golden Gate University',
      type: 'DBA',
      logo: 'https://d2o2utebsixu4k.cloudfront.net/upgrad/new-home/svg/GGU.svg'
    },
    {
      title: 'Doctor of Business Administration from Rushford Business School, Switzerland',
      university: 'Rushford Business School',
      type: 'DBA',
      logo: 'https://d2o2utebsixu4k.cloudfront.net/upgrad/new-home/svg/Rushford.svg'
    },
    {
      title: 'Executive Diploma in Machine Learning and AI',
      university: 'IIIT Bangalore',
      type: 'Diploma',
      logo: 'https://d2o2utebsixu4k.cloudfront.net/upgrad/new-home/svg/IITB.svg'
    },
    {
      title: 'Advanced Certificate Program in Generative AI',
      university: 'IIIT Bangalore',
      type: 'Certificate',
      logo: 'https://d2o2utebsixu4k.cloudfront.net/upgrad/new-home/svg/IITB.svg'
    },
    {
      title: 'Executive Diploma in Data Science & AI',
      university: 'IIIT Bangalore',
      type: 'Diploma',
      logo: 'https://d2o2utebsixu4k.cloudfront.net/upgrad/new-home/svg/IITB.svg'
    },
    {
      title: 'Advanced Certificate in Digital Marketing and Communication',
      university: 'MICA',
      type: 'Certificate',
      logo: 'https://d2o2utebsixu4k.cloudfront.net/upgrad/new-home/svg/MICA.svg'
    },
    {
      title: 'Advanced Certificate in Performance Marketing',
      university: 'MICA',
      type: 'Certificate',
      logo: 'https://d2o2utebsixu4k.cloudfront.net/upgrad/new-home/svg/MICA.svg'
    }
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <a href="/" className="flex items-center">
                <div className="h-10 w-32">
                  <img 
                    src="https://d2o2utebsixu4k.cloudfront.net/upgrad/new-home/svg/upGrad.svg" 
                    alt="upGrad Logo" 
                    className="h-10 w-32"
                  />
                </div>
              </a>
            </div>

            {/* Search Bar */}
            <div className="hidden md:flex flex-1 max-w-md mx-8">
              <div className="relative w-full">
                <input
                  type="search"
                  placeholder="Explore Courses"
                  className="w-full h-11 pl-4 pr-12 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                  <Search className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <div className="relative">
                <button
                  onClick={() => setIsDomainsOpen(!isDomainsOpen)}
                  className="flex items-center text-gray-700 hover:text-blue-600 transition-colors"
                >
                  <span className="text-sm font-medium">Domains</span>
                  <ChevronDown className="ml-1 h-4 w-4" />
                </button>
                
                {isDomainsOpen && (
                  <div className="absolute top-full left-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                    <div className="p-4">
                      <h3 className="text-sm font-medium text-gray-900 mb-3">Browse by Domain</h3>
                      <div className="space-y-2">
                        {domains.map((domain) => (
                          <a
                            key={domain}
                            href="#"
                            className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-blue-600 rounded-md transition-colors"
                          >
                            {domain}
                          </a>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <a href="#" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
                For Business
              </a>
              <a href="#" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
                About Us
              </a>
              <a href="#" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors">
                Contact
              </a>
            </nav>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-700 hover:text-blue-600"
              >
                {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-200">
            <div className="px-4 py-4 space-y-4">
              <div className="relative">
                <input
                  type="search"
                  placeholder="Explore Courses"
                  className="w-full h-10 pl-4 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              </div>
              <div className="space-y-2">
                <a href="#" className="block text-sm font-medium text-gray-700 hover:text-blue-600">Domains</a>
                <a href="#" className="block text-sm font-medium text-gray-700 hover:text-blue-600">For Business</a>
                <a href="#" className="block text-sm font-medium text-gray-700 hover:text-blue-600">About Us</a>
                <a href="#" className="block text-sm font-medium text-gray-700 hover:text-blue-600">Contact</a>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            India's Top Upskilling Platform
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Choose from top online programs in AI, Data Science, MBA, Marketing, Tech. 
            Trusted by 100+ Academic & Industry Partners with Career support and Flexible learning.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors">
              Explore Courses
            </button>
            <button className="border border-blue-600 text-blue-600 px-8 py-3 rounded-lg hover:bg-blue-50 transition-colors">
              Talk to Expert
            </button>
          </div>
        </div>

        {/* Course Categories */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Popular Programs</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {courses.map((course, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow hover-lift">
                <div className="flex items-center mb-4">
                  <img 
                    src={course.logo} 
                    alt={course.university}
                    className="w-12 h-12 rounded-lg border border-gray-200 p-1 bg-white"
                  />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">{course.university}</p>
                    <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                      {course.type}
                    </span>
                  </div>
                </div>
                <h3 className="text-sm font-medium text-gray-900 mb-3 line-clamp-2">
                  {course.title}
                </h3>
                <button className="w-full text-sm text-blue-600 hover:text-blue-700 font-medium">
                  Learn More →
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Section */}
        <div className="bg-gray-50 rounded-2xl p-8 mb-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">100+</div>
              <div className="text-gray-600">Academic & Industry Partners</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">1M+</div>
              <div className="text-gray-600">Learners Worldwide</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">85%</div>
              <div className="text-gray-600">Career Transition Success</div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-blue-600 rounded-2xl p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Career?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of professionals who have upskilled with upGrad
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-blue-600 px-8 py-3 rounded-lg hover:bg-gray-50 transition-colors font-medium">
              Start Learning Today
            </button>
            <button className="border border-white text-white px-8 py-3 rounded-lg hover:bg-white hover:text-blue-600 transition-colors font-medium">
              Download Brochure
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <img 
                src="https://d2o2utebsixu4k.cloudfront.net/upgrad/new-home/svg/upGrad.svg" 
                alt="upGrad Logo" 
                className="h-8 w-24 mb-4"
              />
              <p className="text-gray-400 text-sm">
                India's largest online higher education company
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Programs</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Data Science</a></li>
                <li><a href="#" className="hover:text-white">Machine Learning</a></li>
                <li><a href="#" className="hover:text-white">MBA</a></li>
                <li><a href="#" className="hover:text-white">Marketing</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">About Us</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
                <li><a href="#" className="hover:text-white">Press</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white">Refund Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2024 upGrad Education Private Limited. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
