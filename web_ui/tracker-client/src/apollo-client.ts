import { ApolloClient, InMemoryCache } from '@apollo/client';

const client = new ApolloClient({
    uri: 'http://0.0.0.0:8001/graphql', // Adjust the URI based on your setup
    cache: new InMemoryCache()
});

export default client;