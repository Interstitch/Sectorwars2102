# Translation Workflow Management Guide

**Created**: June 2, 2025  
**Version**: 1.0  
**Status**: Workflow Documentation  

## Overview

This guide provides comprehensive instructions for managing translations in SectorWars 2102, including workflows for developers, translators, and community contributors.

## Translation System Architecture

### Backend Components
- **Translation Service**: Core API for managing translations (`/api/v1/i18n/`)
- **Database Models**: Structured storage for translations and progress tracking
- **Language Detection**: Automatic browser language detection
- **User Preferences**: Persistent language choice storage

### Frontend Components
- **Shared Configuration**: Unified i18n setup for both applications
- **Language Switcher**: User interface for language selection
- **Translation Hooks**: React hooks for accessing translations
- **Namespace Organization**: Feature-based content organization

## Developer Workflow

### 1. Adding New Translatable Content

#### Step 1: Identify Translation Namespace
Choose the appropriate namespace for your content:
- `common`: Shared across applications (buttons, status messages)
- `admin`: Admin UI specific content
- `game`: Player Client specific content
- `auth`: Authentication flows
- `ai`: AI assistant content
- `marketing`: Landing page content
- `errors`: Error messages
- `validation`: Form validation messages

#### Step 2: Add Translation Keys
Add new keys to the appropriate base translation file:

```json
// /shared/i18n/namespaces/admin.json
{
  "newFeature": {
    "title": "New Feature",
    "description": "Description of the new feature",
    "actions": {
      "enable": "Enable Feature",
      "disable": "Disable Feature"
    }
  }
}
```

#### Step 3: Use Translation in Components
```typescript
import { useTranslation } from 'react-i18next';

const MyComponent: React.FC = () => {
  const { t } = useTranslation('admin');
  
  return (
    <div>
      <h2>{t('newFeature.title')}</h2>
      <p>{t('newFeature.description')}</p>
      <button>{t('newFeature.actions.enable')}</button>
    </div>
  );
};
```

#### Step 4: Upload to Database
Use the admin API to upload new translations:

```typescript
// Upload to database via API
const uploadTranslations = async () => {
  const response = await fetch('/api/v1/i18n/admin/bulk/en/admin', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      translations: newFeatureTranslations,
      overwrite: true
    })
  });
};
```

### 2. String Extraction Process

#### Automated Extraction Tool
```bash
# Create extraction tool (future implementation)
npm run extract-strings --app=admin-ui
npm run extract-strings --app=player-client
```

#### Manual Extraction Checklist
1. **Search for hardcoded strings**: Look for text in quotes that users will see
2. **Replace with translation calls**: Use `t('key')` pattern
3. **Handle dynamic content**: Use interpolation `t('key', { variable })`
4. **Add pluralization**: Use `t('key', { count })` for count-dependent text
5. **Test in development**: Verify translations load correctly

### 3. Translation File Management

#### File Structure
```
shared/i18n/
├── locales/
│   ├── en.json (complete base)
│   ├── es.json (translations)
│   ├── fr.json (translations)
│   └── ...
├── namespaces/
│   ├── common.json
│   ├── admin.json
│   ├── game.json
│   └── ...
└── config.ts
```

#### Validation Process
```bash
# Validate translation completeness (future tool)
npm run validate-translations --language=es
npm run find-missing-keys --namespace=admin
```

## Translator Workflow

### 1. Access Translation Management

#### Admin Interface Access
1. Log in to Admin UI with translator permissions
2. Navigate to Settings > Translation Management
3. Select target language and namespace
4. Begin translation work

#### API Access (Advanced)
```bash
# Get current translations
curl -X GET "/api/v1/i18n/es/admin" \
  -H "Authorization: Bearer $TOKEN"

# Update specific translation
curl -X POST "/api/v1/i18n/admin/translation/es/admin" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "key": "dashboard.title",
    "value": "Panel de Control Central",
    "context": "Main dashboard page title"
  }'
```

### 2. Translation Guidelines

#### Quality Standards
1. **Accuracy**: Translate meaning, not just words
2. **Consistency**: Use established terminology throughout
3. **Context Awareness**: Consider UI space constraints
4. **Cultural Appropriateness**: Adapt for target culture
5. **Gaming Terminology**: Use established gaming terms

#### Translation Process
1. **Review Context**: Understand where text appears in application
2. **Check Constraints**: Consider character limits and UI layout
3. **Maintain Tone**: Preserve intended tone and formality level
4. **Test in Context**: Preview translations in actual interface
5. **Verify Completeness**: Ensure all required keys are translated

### 3. Cultural Adaptation Guidelines

#### Language-Specific Considerations

**Spanish (es)**
- Use formal "usted" for system messages
- Adapt currency and number formats
- Consider regional variations (Spain vs. Latin America)

**Chinese Simplified (zh-CN)**
- Use appropriate formality levels
- Adapt for simplified character set
- Consider cultural context for gaming terminology

**French (fr)**
- Maintain French language purity regulations
- Use appropriate formal/informal address
- Adapt for French Canadian if needed

**Portuguese (pt)**
- Consider Brazilian Portuguese conventions
- Adapt gaming terminology appropriately
- Use correct formality levels

### 4. Progress Tracking

#### Completion Metrics
- **Namespace Progress**: Track completion by feature area
- **Overall Progress**: Monitor total translation completeness
- **Quality Metrics**: Track verified vs. unverified translations
- **Update Frequency**: Monitor when translations last updated

#### Reporting
```bash
# Get progress report
curl -X GET "/api/v1/i18n/admin/progress/es" \
  -H "Authorization: Bearer $TOKEN"
```

## Community Contributor Workflow

### 1. Getting Started

#### Registration Process
1. Create account on SectorWars 2102
2. Request translator permissions via support
3. Complete translation guidelines training
4. Receive access to translation tools

#### Contribution Guidelines
1. **Start Small**: Begin with common/simple translations
2. **Follow Style Guide**: Maintain consistency with existing translations
3. **Collaborate**: Coordinate with other translators for your language
4. **Test Changes**: Preview translations before submitting
5. **Document Issues**: Report problems with source text or context

### 2. Collaboration Tools

#### Translation Discussions
- **Language Teams**: Join language-specific teams for coordination
- **Review Process**: Peer review for translation quality
- **Issue Tracking**: Report and resolve translation issues
- **Style Guides**: Maintain language-specific style guidelines

#### Quality Assurance
1. **Peer Review**: Other translators review contributions
2. **Native Speaker Validation**: Native speakers approve translations
3. **Context Testing**: Test translations in actual application
4. **Feedback Integration**: Incorporate user feedback and corrections

### 3. Recognition System

#### Contributor Credits
- **Translation Credits**: Recognition for contributed translations
- **Community Leaderboards**: Top contributors by language
- **Quality Ratings**: Recognition for high-quality translations
- **Special Badges**: In-game recognition for translators

## Technical Implementation

### 1. API Reference

#### Public Endpoints
```typescript
GET    /api/v1/i18n/languages           // List supported languages
GET    /api/v1/i18n/detect              // Auto-detect language
GET    /api/v1/i18n/{lang}              // Get all translations
GET    /api/v1/i18n/{lang}/{namespace}  // Get namespace translations
```

#### User Endpoints
```typescript
GET    /api/v1/i18n/user/preference     // Get user language preference
POST   /api/v1/i18n/user/preference     // Set user language preference
GET    /api/v1/i18n/user/ai-context     // Get AI language context
```

#### Admin Endpoints
```typescript
GET    /api/v1/i18n/admin/progress/{lang}           // Get translation progress
POST   /api/v1/i18n/admin/translation/{lang}/{ns}   // Update translation
POST   /api/v1/i18n/admin/bulk/{lang}/{ns}          // Bulk import
POST   /api/v1/i18n/admin/initialize                // Initialize system
```

### 2. Database Schema

#### Core Tables
```sql
-- Language configuration
CREATE TABLE languages (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    direction VARCHAR(3) DEFAULT 'ltr',
    is_active BOOLEAN DEFAULT TRUE,
    completion_percentage INTEGER DEFAULT 0
);

-- Translation content
CREATE TABLE translation_keys (
    id SERIAL PRIMARY KEY,
    key VARCHAR(200) NOT NULL,
    language_id INTEGER REFERENCES languages(id),
    namespace_id INTEGER REFERENCES translation_namespaces(id),
    value TEXT NOT NULL,
    context TEXT,
    is_verified BOOLEAN DEFAULT FALSE
);

-- User preferences
CREATE TABLE user_language_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    language_id INTEGER REFERENCES languages(id),
    manual_override BOOLEAN DEFAULT FALSE
);
```

### 3. Frontend Integration

#### React Hook Usage
```typescript
// Basic usage
const { t } = useTranslation('namespace');
const text = t('key');

// With interpolation
const message = t('welcome', { name: 'John' });

// With pluralization
const count = t('items', { count: 5 });

// With default value
const text = t('key', { defaultValue: 'Default text' });
```

#### Language Switching
```typescript
import { changeLanguage } from 'shared/i18n';

const switchLanguage = async (languageCode: string) => {
  await changeLanguage(languageCode);
  // Language changed and preference saved
};
```

## Best Practices

### 1. Development Best Practices

#### Translation Key Naming
- Use hierarchical keys: `dashboard.stats.totalUsers`
- Be descriptive: `buttons.saveAndContinue` not `buttons.save2`
- Group related content: `forms.validation.required`
- Use consistent naming patterns

#### Code Organization
- Import translations at component level
- Use meaningful variable names for translated text
- Group translation calls logically
- Handle loading states properly

#### Performance Considerations
- Use namespace loading for large applications
- Implement lazy loading for unused namespaces
- Cache translations appropriately
- Minimize translation calls in render loops

### 2. Translation Best Practices

#### Content Guidelines
- Write clear, concise source text
- Provide context for translators
- Consider text expansion/contraction
- Plan for right-to-left languages
- Use placeholder text appropriately

#### Quality Assurance
- Implement peer review process
- Test translations in context
- Validate with native speakers
- Monitor user feedback
- Update based on usage patterns

### 3. Maintenance Best Practices

#### Regular Maintenance
- Monitor translation completion
- Update outdated translations
- Remove unused translation keys
- Validate translation accuracy
- Backup translation database

#### Community Management
- Recognize contributor efforts
- Provide clear guidelines
- Facilitate collaboration
- Resolve conflicts fairly
- Maintain quality standards

## Troubleshooting

### Common Issues

#### Missing Translations
- **Symptom**: Translation key displayed instead of text
- **Solution**: Add translation to appropriate namespace
- **Prevention**: Validate completeness before deployment

#### Incorrect Language Detection
- **Symptom**: Wrong language displayed automatically
- **Solution**: Check browser language headers and detection logic
- **Prevention**: Test with various browser configurations

#### Performance Issues
- **Symptom**: Slow language switching or translation loading
- **Solution**: Implement caching and lazy loading
- **Prevention**: Monitor performance metrics

#### Cultural Inappropriateness
- **Symptom**: User feedback about cultural issues
- **Solution**: Review with cultural consultants
- **Prevention**: Include cultural review in translation process

### Support Resources

#### Documentation
- API documentation: `/api/v1/docs`
- Translation guidelines: This document
- Developer guides: `/docs/development/`
- Community forums: Support section

#### Contact Information
- Technical issues: development team
- Translation questions: translation coordinators
- Community support: community managers
- Cultural concerns: cultural consultants

---

*This workflow guide is maintained by the SectorWars 2102 development team and updated regularly to reflect current best practices.*