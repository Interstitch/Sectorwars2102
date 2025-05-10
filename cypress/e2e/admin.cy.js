
describe('Admin Panel', () => {
  beforeEach(() => {
    // Reset database
    cy.request('POST', '/test/reset')
    
    // Create admin user and test data
    cy.request('POST', '/test/setup', {
      user: {
        username: 'admin',
        email: 'admin@test.com',
        password: 'admin',
        is_admin: true
      },
      sector: {
        id: 1,
        name: 'Terra Prime',
        has_planet: true,
        port_data: {
          buy: { Food: 100 },
          sell: { Food: 80 },
          inventory: { Food: 1000 }
        },
        links: [2, 3]
      }
    })

    // Login
    cy.visit('/login')
    cy.get('input[name="username"]').type('admin')
    cy.get('input[name="password"]').type('admin')
    cy.get('form').submit()
  })

  it('should display and interact with universe visualization', () => {
    cy.visit('/admin')
    
    // Check container exists
    cy.get('#universe-map').should('be.visible')
    
    // Check SVG and its elements
    cy.get('.universe-svg').should('exist')
    cy.get('.universe-container').should('exist')
    cy.get('.sector-node').should('have.length.at.least', 1)
    cy.get('.sector-link').should('have.length.at.least', 1)
    
    // Check sector node properties
    cy.get('.sector-node').first()
      .should('have.attr', 'data-sector-id')
      .and('not.be.empty')
    
    // Test click interaction
    cy.get('.sector-node').first().click()
    cy.get('.sector-info')
      .should('be.visible')
      .within(() => {
        cy.get('h3').should('contain', 'Sector')
        cy.get('.edit-group').should('have.length.at.least', 1)
      })
  })
})
