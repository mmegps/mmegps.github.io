---
layout: post
title: Myths around the AI bandwagon
---

| ![]({{ site.baseurl }}/images/MM3.png ) |
| :-------------------------------------: |
|         _(c) 2017 Mohit Mehta_          |

Every start-up today wants to be an AI start-up. That's great.

AI is the future and with more data and compute we definitely have more predictive power at our disposal leading to novel applications. AI is a revolution and the party is just getting started.

With so much promise around, there also exist some myths and misconceptions in the industry which we should be conscious of. The objective of this post is to increase awareness around AI/ML and how you and your organisation can take a lead.

**Myth 1: More data means better outcomes**  
Having large amounts of labelled training data is great and often a pre-requisite for training useful models. But, it is not the quantity of data which is important but the quality. By quality data, I mean more than the data curation, cleaning and augmentation which is expected in most ML pipelines. But the variation, the balance and the coverage the dataset to answer the business problem/need in question. At an intuitive level, think of an ML model as fitting a curve, given some data points. If some interesting data points are missing, then the model cannot be expected to account for them and generate a useful prediction.

In practical terms consider a chatbot application for a customer support system. If a wide variety of scenarios and variations are not covered in sufficient numbers and depth when collecting the data, it will not be possible to train a model which performs well when deployed in practice. So, having thousands of call records is great, but the quality of what these record contain in them is of paramount importance to make a useful system out of it.

**Myth 2: Models are forever**  
It is said, data is the new oil, which is sort-of correct, but it also burns. Once a model is trained with available data, it is functional. But, it is also carries the inherent assumptions and biases which were embedded within the training data, therefore when the underlying assumptions change and evolve, the model will also loose its utility.

Consider a forecasting system for an online retailer. Even leaving extraordinary situations like the current pandemic aside, a model trained with data from the consumer demand continuously varies with the trends of the season. Therefore any model predictions which are fruitful and on-target this year, may not yield same level of efficacy when utilised next year.

The understanding required for this is continuous data feed and retraining cycles, which give a model best chance on what’s happening out there, and how to react best to altering market conditions.

**Myth 3: One size fits all**  
The current approaches (and achievements) for AI/ML are problem centric and pretty narrow. They are designed for a specific problem, given data which has some predictive power over this very problem.

As an illustration, a model trained to detect apples within an image, cannot detect oranges. Further, a model to detect "Granny Smith" apples will have very low confidence when given a "Gala" apple to detect. It will require further training (although not as much) with the new type to able to differentiate and be useful.

The technique touched upon here, basically retraining a pre-trained network for new scenarios with limited additional data, is called transfer learning and has shown a lot of promise. It is already a starting point for many real-world applications.

So, when there is a discussion on AI/ML next in your organisation, contribute with an educated understanding and appraisal of where the bounds are today. This will elevate the collective understanding of your team and help making a move in the direction where you get the most bang for the buck, and also deliver real and useful value to your clients.

The AI revolution is just getting started…

Note: This post was first published on LinkedIn [here](https://www.linkedin.com/pulse/myths-from-ai-bandwagon-mohit-mehta-phd/)
