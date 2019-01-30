require 'phraseapp-ruby'
require 'yaml'

configuration = YAML.load(File.read("PhraseApp_configuration.yaml"))

if configuration[:migrate_from_ios_to_android]
  project_a_keys = configuration[:ios_keys]
  project_b_keys = configuration[:android_keys]
  project_a = configuration[:project_ios]
  project_b = configuration[:project_android]
else
  project_a_keys = configuration[:android_keys]
  project_b_keys = configuration[:ios_keys]
  project_a = configuration[:project_android]
  project_b = configuration[:project_ios]
end

# Setup Authentication Credentials and Client
credentials = PhraseApp::Auth::Credentials.new(token: configuration[:API_ACCESS_TOKEN])
client = PhraseApp::Client.new(credentials)

# Fetch keys from the project
#
def fetch_keys(client, project_id, keys)
  fetched_keys = []
  keys.each do |key|
    found_key, err = client.keys_list(project_id, 1, 1, PhraseApp::RequestParams::KeysListParams.new(q: "name:#{key}"))
    if err
      raise err.inspect
    end
    if found_key.empty? or found_key.first.name != key
      raise "Could not find key with name #{key}"
    end
    fetched_keys.push(found_key.first)
  end
  return fetched_keys
end

# Create new keys in the project
# If key is exist delete it first and create a new one
#
def create_keys(client, project_id, keys)
  created_keys = []
  keys.each do |key|
    new_key, _ = client.key_create(project_id, PhraseApp::RequestParams::TranslationKeyParams.new(name: key, tags: [], plural:false))
    if new_key.nil?
      existing_key = fetch_keys(client, project_id, [key]).first
      client.key_delete(project_id, existing_key.id)
      new_key, _ = client.key_create(project_id, PhraseApp::RequestParams::TranslationKeyParams.new(name: key, tags: [], plural:false))
    end
    created_keys.push(new_key)
  end
  return created_keys
end

# Copying translations
#
def copy_translations(client, project_id, keys)
  copied_translations = []
  keys.each do |key|
    translations, err = client.translations_by_key(project_id, key.id, page=1, per_page=100, PhraseApp::RequestParams::TranslationsListParams.new)

    if err
      raise err.inspect
    end

    if translations.empty?
      raise "Could not find translations to copy"
    end
    copied_translations.push(translations)
  end
  return copied_translations
end

def fetch_locales(client, project_id)
  locales, err = client.locales_list(project_id, page=1, per_page=100, PhraseApp::RequestParams::TranslationsListParams.new)
  if err
    raise err.inspect
  end
  locales = locales.inject({}) do |hash, locale|
    hash[locale.name] = locale
    hash
  end
  return locales
end

def apply(client, project_id, translations, locales, keys)
    translations.each_with_index do |translation, index|
      key = keys[index]
      translation.each { |t|
        unless t.content.nil? || t.content.empty?
          locale_in_b = locales[t.locale["name"]]
          raise "There is no locale with name '#{t.locale["name"]}' in the project with id #{project_id}" unless locale_in_b
          rsp, err = client.translation_create(
              project_id,
              PhraseApp::RequestParams::TranslationParams.new(
                  content: t.content,
                  key_id: key.id,
                  excluded: t.excluded,
                  locale_id: locale_in_b.id,
                  plural_suffix: t.plural_suffix,
                  unverified: t.unverified
              )
          )
          if err
            raise err.inspect
          end
        end
      }
      puts "Translations for #{key.name} migrated."
  end
end

##Execute
#
fetched_keys = fetch_keys(client, project_a, project_a_keys)
created_keys = create_keys(client, project_b, project_b_keys)
copied_translations = copy_translations(client, project_a, fetched_keys)
fetched_locales = fetch_locales(client, project_b)
apply(client, project_b, copied_translations, fetched_locales, created_keys)

puts "All translations were copied!"
