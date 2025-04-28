import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import styled from 'styled-components';

const LayoutContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const Header = styled.header`
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
`;

const Logo = styled.div`
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color);
`;

const Nav = styled.nav`
  display: flex;
  gap: 1.5rem;
  align-items: center;
`;

const NavItem = styled(NavLink)`
  color: var(--text-color);
  font-weight: 500;
  text-decoration: none;
  padding: 0.5rem 0;
  position: relative;

  &:hover {
    color: var(--primary-color);
    text-decoration: none;
  }

  &.active {
    color: var(--primary-color);
    
    &:after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 2px;
      background-color: var(--primary-color);
    }
  }
`;

const LogoutButton = styled.button`
  background: none;
  border: none;
  color: var(--text-color);
  font-weight: 500;
  cursor: pointer;
  padding: 0.5rem 0;

  &:hover {
    color: var(--error-color);
  }
`;

const Main = styled.main`
  flex: 1;
  padding: 2rem 0;
`;

const MainContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
`;

const Footer = styled.footer`
  background-color: white;
  padding: 1.5rem 0;
  border-top: 1px solid var(--border-color);
`;

const FooterContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-light);
  font-size: 0.875rem;
`;

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <LayoutContainer>
      <Header>
        <HeaderContent>
          <Logo>Cloud Image API</Logo>
          <Nav>
            <NavItem to="/" end>Dashboard</NavItem>
            <NavItem to="/upload">Upload</NavItem>
            <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
          </Nav>
        </HeaderContent>
      </Header>
      
      <Main>
        <MainContent>
          <Outlet />
        </MainContent>
      </Main>
      
      <Footer>
        <FooterContent>
          <div>© {new Date().getFullYear()} Cloud Image API</div>
          <div>A Cloudinary-like service built with FastAPI and React</div>
        </FooterContent>
      </Footer>
    </LayoutContainer>
  );
};

export default Layout;
