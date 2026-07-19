import pandas as pd
from surprise import SVD, Dataset, Reader
from app.models import Rating, Item, db
import logging

logger = logging.getLogger(__name__)

class CollaborativeRecommender:
    def __init__(self):
        self.model = None
        self.item_ids = []
        self._train()

    def _train(self):
        ratings = Rating.query.all()
        if not ratings:
            self.model = None
            self.item_ids = []
            return

        df = pd.DataFrame([(r.user_id, r.item_id, r.score) for r in ratings],
                          columns=['user_id', 'item_id', 'rating'])
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[['user_id', 'item_id', 'rating']], reader)

        self.model = SVD(n_factors=50, n_epochs=20, verbose=False)
        trainset = data.build_full_trainset()
        self.model.fit(trainset)

        self.item_ids = [item.id for item in Item.query.all()]
        logger.info('Modelo SVD entrenado con %d ítems', len(self.item_ids))

    def refresh(self):
        self._train()

    def recommend_for_user(self, user_id, top_n=5):
        if not self.model or not self.item_ids:
            return []

        rated_ids = [r.item_id for r in Rating.query.filter_by(user_id=user_id).all()]
        candidates = [item_id for item_id in self.item_ids if item_id not in rated_ids]

        if not candidates:
            return []

        predictions = []
        for item_id in candidates:
            pred = self.model.predict(user_id, item_id).est
            predictions.append((item_id, pred))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return [item_id for item_id, _ in predictions[:top_n]]
