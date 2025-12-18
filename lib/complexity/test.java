    @Autowired
    PetGroupHandler petGroupHandler;

    @Bean
    public JdbcMessageStore jdbcMessageStore(
            @Qualifier("mydbDataSource") DataSource dataSource) {
        JdbcMessageStore messageStore = new JdbcMessageStore(dataSource);
        messageStore.setRegion("petstore-pubsub");
        return messageStore;
    }

    @Bean
    IntegrationFlow petStoreSubscriptionFlow(JdbcMessageStore jdbcMessageStore, PetOutputProcessor petOutputProcessor) {
        return IntegrationFlow.from("petStoreSubscriptionMessageChannel")
                .filter(petOfInterestFilter, "shouldProcess")
                .aggregate(aggregatorSpec -> aggregatorSpec
                        .messageStore(jdbcMessageStore)
                        .outputProcessor(petOutputProcessor)
                        .expireGroupsUponCompletion(true) 
                        .groupTimeout(300 * 1000) // 5 minutes
                        .sendPartialResultOnExpiry(true) // send partial group
                        .correlationStrategy(message -> ((Pet) message.getPayload()).getBreed())
                        .releaseStrategy(group -> group.size()>=2))
                .handle(petGroupHandler, "handle")
                .get();