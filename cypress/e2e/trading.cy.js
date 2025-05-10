
describe('Trading Flow', () => {
  beforeEach(() => {
    // Reset database and create test data
    cy.request('POST', '/test/reset')
    cy.request('POST', '/test/setup', {
      user: {
        username: 'test_trader',
        email: 'test@trader.com',
        password: 'password123',
        credits: 1000,
        location: 1,
        ship_type: 'Light Freighter',
        ship_name: 'SS Test Trader'
      },
      sector: {
        id: 1,
        name: 'Test Sector',
        has_planet: true,
        port_data: {
          buy: { Food: 100 },
          sell: { Food: 80 },
          inventory: { Food: 1000 },
          ships: {}
        },
        links: [2, 3, 4]
      }
    })
  })

  it('should handle complete trading flow', () => {
    // Login
    cy.visit('/login')
    cy.get('input[name="username"]').type('test_trader')
    cy.get('input[name="password"]').type('password123')
    cy.get('form').submit()

    // Dock at port
    cy.get('button').contains('Dock').click()
    
    // Initial credits check
    cy.get('.credits').invoke('text').then((text) => {
      const initialCredits = parseInt(text.match(/\d+/)[0])
      
      // Buy food
      const foodAmount = 5
      const foodPrice = 80
      cy.get('input[name="amount"]').type(foodAmount)
      cy.get('button').contains('Buy Food').click()

      // Verify credits were deducted
      const expectedCredits = initialCredits - (foodPrice * foodAmount)
      cy.get('.credits').should('contain', expectedCredits)

      // Verify cargo was added
      cy.get('.cargo').should('contain', 'Food')
      cy.get('.cargo').should('contain', foodAmount)

      // Sell food back
      cy.get('input[name="amount"]').type(foodAmount)
      cy.get('button').contains('Sell Food').click()

      // Verify final credits
      const expectedFinalCredits = initialCredits + ((100 - foodPrice) * foodAmount)
      cy.get('.credits').should('contain', expectedFinalCredits)

      // Verify cargo was removed
      cy.get('.cargo').should('not.contain', 'Food')
    })
  })
})
