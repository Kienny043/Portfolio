import { useEffect } from 'react'
import { apiPost, useApi } from './lib/api'
import About from './components/About'
import Blog from './components/Blog'
import Contact from './components/Contact'
import Experience from './components/Experience'
import Footer from './components/Footer'
import Hero from './components/Hero'
import Nav from './components/Nav'
import Projects from './components/Projects'
import Skills from './components/Skills'
import Testimonials from './components/Testimonials'

const rows = (state) => (state.status === 'success' ? state.data : [])

// Log one visit per page load. Production only, so dev reloads don't inflate the count.
let visitLogged = false
function useVisitLog() {
  useEffect(() => {
    if (!import.meta.env.PROD || visitLogged) return
    visitLogged = true
    apiPost('/analytics/').catch(() => {})
  }, [])
}

export default function App() {
  const profile = useApi('/profile/')
  const education = useApi('/education/')
  const skills = useApi('/skills/')
  const experience = useApi('/experience/')
  const projects = useApi('/projects/')
  const testimonials = useApi('/testimonials/')
  const blog = useApi('/blog/')
  useVisitLog()

  // Sections that render nothing when empty are dropped from the numbering and the nav.
  const showSkills = skills.status !== 'success' || skills.data.length > 0
  const showExperience = experience.status !== 'success' || experience.data.length > 0
  const showProjects = projects.status !== 'success' || projects.data.length > 0
  const showTestimonials = testimonials.status !== 'success' || testimonials.data.length > 0
  const showBlog = blog.status !== 'success' || blog.data.length > 0

  const sections = [
    { id: 'about', label: 'About', show: true },
    { id: 'skills', label: 'Skills', show: showSkills },
    { id: 'experience', label: 'Experience', show: showExperience },
    { id: 'projects', label: 'Projects', show: showProjects },
    { id: 'testimonials', label: 'Testimonials', show: showTestimonials },
    { id: 'blog', label: 'Blog', show: showBlog },
    { id: 'contact', label: 'Contact', show: true },
  ].filter((s) => s.show)
  const num = (id) => sections.findIndex((s) => s.id === id) + 1

  const owner = rows(profile)[0]
  const name = owner ? [owner.firstname, owner.lastname].filter(Boolean).join(' ') : ''

  return (
    <>
      <Nav links={sections} />
      <main>
        <Hero />
        <About number={num('about')} profile={profile} education={education} />
        <Skills number={num('skills')} skills={skills} />
        <Experience number={num('experience')} experience={experience} />
        <Projects number={num('projects')} projects={projects} />
        {showTestimonials && (
          <Testimonials number={num('testimonials')} testimonials={testimonials} />
        )}
        {showBlog && <Blog number={num('blog')} blog={blog} />}
        <Contact number={num('contact')} />
      </main>
      <Footer name={name} />
    </>
  )
}
