from rootzengine.ml.trainer import train_model

def test_train_model_default(monkeypatch):
    # prevent actual printing
    monkeypatch.setattr('builtins.print', lambda *args, **kwargs: None)
    train_model(None)
    # passes if no exceptions
