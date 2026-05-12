import { ShaderGradient, ShaderGradientCanvas } from '@shadergradient/react';
import { useMemo, useState, useRef } from 'react';
import { User, Mail, LogIn } from 'lucide-react';
import loginLogo from '../../assets/Image_20260513001106_704_33.png';

// ── TEST MODE: Set to true to bypass credential validation ──
const SKIP_CREDENTIALS = true;

export default function App() {
  const [role, setRole] = useState('student');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [showEmailDropdown, setShowEmailDropdown] = useState(false);
  const emailInputRef = useRef(null);

  const emailRule = useMemo(() => {
    return role === 'student'
      ? { suffix: '@link.cuhk.edu.cn', next: '/students-interface/student_dashboard_index.html' }
      : { suffix: '@cuhk.edu.cn', next: '/aa_dashboard.html' };
  }, [role]);

  const emailValid = SKIP_CREDENTIALS || email.toLowerCase().endsWith(emailRule.suffix);
  const nameValid = SKIP_CREDENTIALS || fullName.trim();

  function onSubmit(e) {
    e.preventDefault();
    if (!nameValid || !emailValid) return;

    const session = {
      role,
      name: fullName.trim() || `Test ${role}`,
      fullName: fullName.trim() || `Test ${role}`,
      email: email.trim() || `test@${role}.local`,
      loginAt: new Date().toISOString(),
    };

    sessionStorage.setItem('cuhksz_user_session', JSON.stringify(session));

    window.location.href = emailRule.next;
  }

  return (
    <main className="app-shell">
      <div aria-hidden="true" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
        <ShaderGradientCanvas style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
          <ShaderGradient
            animate="on"
            axesHelper="on"
            bgColor1="#000000"
            bgColor2="#000000"
            brightness={1.1}
            cAzimuthAngle={180}
            cDistance={3.9}
            cPolarAngle={115}
            cameraZoom={1}
            color1="#429aff"
            color2="#2631fe"
            color3="#000086"
            destination="onCanvas"
            embedMode="off"
            envPreset="city"
            format="gif"
            fov={45}
            frameRate={10}
            gizmoHelper="hide"
            grain="off"
            lightType="3d"
            pixelDensity={1}
            positionX={-0.5}
            positionY={0.1}
            positionZ={0}
            range="disabled"
            rangeEnd={40}
            rangeStart={0}
            reflection={0.1}
            rotationX={0}
            rotationY={0}
            rotationZ={235}
            shader="defaults"
            type="waterPlane"
            uAmplitude={0}
            uDensity={1.1}
            uFrequency={5.5}
            uSpeed={0.1}
            uStrength={2.4}
            uTime={0.2}
            wireframe={false}
          />
        </ShaderGradientCanvas>
      </div>

      <section className="login-shell">
        <div className="login-card">
          <div className="login-brand">
            <img className="login-logo" src={loginLogo} alt="Student Study Progress Dashboard logo" />
            <div>
              <p className="eyebrow">Chinese University of Hong Kong, Shenzhen</p>
              <h1>Student Study Progress Dashboard</h1>
              <p className="subtitle">
                See your skills, track your progress, own your learning.
              </p>
            </div>
          </div>

          <div className="role-toggle">
            <button
              type="button"
              className={role === 'student' ? 'active' : ''}
              onClick={() => setRole('student')}
            >
              I am a Student
            </button>
            <button
              type="button"
              className={role === 'advisor' ? 'active' : ''}
              onClick={() => setRole('advisor')}
            >
              Academic Advisor
            </button>
          </div>

          <form className="auth-form" onSubmit={onSubmit}>
            <label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <User size={18} />
                Full Name
              </div>
              <input
                type="text"
                placeholder="e.g. John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </label>

            <label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <Mail size={18} />
                Campus Email
              </div>
              <div style={{ position: 'relative' }}>
                <input
                  ref={emailInputRef}
                  type="email"
                  placeholder={`yourname${emailRule.suffix}`}
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setShowEmailDropdown(e.target.value.includes('@'));
                  }}
                  onBlur={() => setTimeout(() => setShowEmailDropdown(false), 200)}
                />
                {showEmailDropdown && email.includes('@') && (
                  <div
                    style={{
                      position: 'absolute',
                      top: '100%',
                      left: 0,
                      right: 0,
                      backgroundColor: 'white',
                      border: '1px solid #d1d5db',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                      zIndex: 10,
                      marginTop: '4px',
                    }}
                  >
                    <div
                      onClick={() => {
                        const username = email.split('@')[0];
                        setEmail(username + emailRule.suffix);
                        setShowEmailDropdown(false);
                      }}
                      style={{
                        padding: '12px 16px',
                        cursor: 'pointer',
                        color: '#374151',
                        fontSize: '14px',
                      }}
                      onMouseOver={(e) => (e.target.style.backgroundColor = '#f3f4f6')}
                      onMouseOut={(e) => (e.target.style.backgroundColor = 'transparent')}
                    >
                      {email.split('@')[0]}
                      {emailRule.suffix}
                    </div>
                  </div>
                )}
              </div>
            </label>
            <small className={email && !emailValid ? 'hint error' : 'hint'}>
              Must end with <code>{emailRule.suffix}</code>
            </small>

            <button type="submit" disabled={SKIP_CREDENTIALS ? false : (!fullName.trim() || !emailValid)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
              <LogIn size={18} />
              Continue with CUHK SSO
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
